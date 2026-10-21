"""Concrete Spotify repository implementation.

Uses ``httpx`` (async) to talk to the Spotify Web API, validates the raw
payloads with Pydantic v2 before mapping them into domain entities, and
translates ``httpx``/HTTP errors into domain exceptions. This is the only
place in the codebase that knows Spotify's wire format.
"""

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.application.interfaces.spotify_repository import SpotifyRepository
from app.domain.entities.album import Album
from app.domain.entities.artist import Artist
from app.domain.entities.image import Image
from app.domain.entities.track import Track
from app.domain.exceptions.spotify_errors import (
    SpotifyError,
    SpotifyInvalidResponseError,
    SpotifyNotFoundError,
    SpotifyRateLimitError,
    SpotifyServiceUnavailableError,
)
from app.infrastructure.external.spotify_auth import SpotifyAuth

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


class _ImagePayload(BaseModel):
    """Raw image object from Spotify."""

    model_config = ConfigDict(extra="ignore")

    url: str
    height: int | None = None
    width: int | None = None


class _ExternalUrlsPayload(BaseModel):
    """Raw external URLs object from Spotify."""

    model_config = ConfigDict(extra="ignore")

    spotify: str = ""


class _ArtistPayload(BaseModel):
    """Raw artist object from Spotify."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    uri: str
    external_urls: _ExternalUrlsPayload = Field(
        default_factory=_ExternalUrlsPayload
    )
    images: list[_ImagePayload] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    popularity: int = 0
    followers: dict[str, Any] | None = None


class _AlbumPayload(BaseModel):
    """Raw album object from Spotify."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    album_type: str
    total_tracks: int
    images: list[_ImagePayload] = Field(default_factory=list)
    release_date: str = ""
    artists: list[_ArtistPayload] = Field(default_factory=list)
    external_urls: _ExternalUrlsPayload = Field(
        default_factory=_ExternalUrlsPayload
    )


class _TrackPayload(BaseModel):
    """Raw track object from Spotify."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    duration_ms: int
    popularity: int
    preview_url: str | None = None
    explicit: bool
    track_number: int
    disc_number: int
    album: _AlbumPayload
    artists: list[_ArtistPayload] = Field(default_factory=list)
    external_urls: _ExternalUrlsPayload = Field(
        default_factory=_ExternalUrlsPayload
    )


class _TopTracksResponse(BaseModel):
    """Raw response for the artist top-tracks endpoint."""

    model_config = ConfigDict(extra="ignore")

    tracks: list[_TrackPayload] = Field(default_factory=list)


def _image_from_payload(payload: _ImagePayload) -> Image:
    """Map a raw image payload into a domain :class:`Image`.

    Args:
        payload: Validated raw image payload.

    Returns:
        The corresponding domain entity.
    """
    return Image(url=payload.url, height=payload.height, width=payload.width)


def _external_urls_dict(payload: _ExternalUrlsPayload) -> dict[str, str]:
    """Convert a validated external-URLs payload into a plain dict.

    Args:
        payload: Validated external URLs payload.

    Returns:
        Mapping of service name to URL.
    """
    return {"spotify": payload.spotify} if payload.spotify else {}


def _artist_from_payload(payload: _ArtistPayload) -> Artist:
    """Map a raw artist payload into a domain :class:`Artist`.

    Args:
        payload: Validated raw artist payload.

    Returns:
        The corresponding domain entity.
    """
    followers = 0
    if isinstance(payload.followers, dict):
        total = payload.followers.get("total")
        if isinstance(total, int):
            followers = total
    return Artist(
        id=payload.id,
        name=payload.name,
        uri=payload.uri,
        external_urls=_external_urls_dict(payload.external_urls),
        images=[_image_from_payload(image) for image in payload.images],
        genres=list(payload.genres),
        popularity=payload.popularity,
        followers=followers,
    )


def _album_from_payload(payload: _AlbumPayload) -> Album:
    """Map a raw album payload into a domain :class:`Album`.

    Args:
        payload: Validated raw album payload.

    Returns:
        The corresponding domain entity.
    """
    return Album(
        id=payload.id,
        name=payload.name,
        album_type=payload.album_type,
        total_tracks=payload.total_tracks,
        images=[_image_from_payload(image) for image in payload.images],
        release_date=payload.release_date,
        artists=[_artist_from_payload(artist) for artist in payload.artists],
        external_urls=_external_urls_dict(payload.external_urls),
    )


def _track_from_payload(payload: _TrackPayload) -> Track:
    """Map a raw track payload into a domain :class:`Track`.

    Args:
        payload: Validated raw track payload.

    Returns:
        The corresponding domain entity.
    """
    return Track(
        id=payload.id,
        name=payload.name,
        duration_ms=payload.duration_ms,
        popularity=payload.popularity,
        preview_url=payload.preview_url,
        explicit=payload.explicit,
        track_number=payload.track_number,
        disc_number=payload.disc_number,
        album=_album_from_payload(payload.album),
        artists=[_artist_from_payload(artist) for artist in payload.artists],
        external_urls=_external_urls_dict(payload.external_urls),
    )


class SpotifyClient(SpotifyRepository):
    """Async Spotify Web API client implementing ``SpotifyRepository``."""

    def __init__(
        self,
        auth: SpotifyAuth,
        timeout_seconds: float = 10.0,
    ) -> None:
        """Initialize the client.

        Args:
            auth: Authentication helper that provides access tokens.
            timeout_seconds: Per-request HTTP timeout.
        """
        self._auth = auth
        self._timeout_seconds = timeout_seconds

    async def _authorized_get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """Perform an authenticated GET request against the Spotify API.

        Args:
            path: API path relative to the base URL (e.g. ``/artists/...``).
            params: Query parameters.

        Returns:
            The parsed JSON body as a dictionary.

        Raises:
            SpotifyNotFoundError: On HTTP 404.
            SpotifyRateLimitError: On HTTP 429.
            SpotifyServiceUnavailableError: On HTTP 5xx or network errors.
            SpotifyError: On any other unexpected error.
            SpotifyInvalidResponseError: If the body is not valid JSON.
        """
        token = await self._auth.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{SPOTIFY_API_BASE_URL}{path}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            raise SpotifyServiceUnavailableError(
                "Could not reach Spotify API"
            ) from exc

        self._raise_for_status(response)

        try:
            body = response.json()
        except ValueError as exc:
            raise SpotifyInvalidResponseError(
                "Spotify returned a non-JSON response"
            ) from exc

        if not isinstance(body, dict):
            raise SpotifyInvalidResponseError(
                "Spotify returned an unexpected response shape"
            )
        return body

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Translate a non-2xx HTTP response into a domain exception.

        Args:
            response: The raw HTTP response.

        Raises:
            SpotifyNotFoundError: On HTTP 404.
            SpotifyRateLimitError: On HTTP 429.
            SpotifyServiceUnavailableError: On HTTP 5xx.
            SpotifyError: On any other non-2xx status.
        """
        status = response.status_code
        if 200 <= status < 300:
            return
        if status == 404:
            raise SpotifyNotFoundError("Spotify resource not found")
        if status == 429:
            raise SpotifyRateLimitError("Spotify rate limit exceeded")
        if status >= 500:
            raise SpotifyServiceUnavailableError(
                "Spotify API is currently unavailable"
            )
        raise SpotifyError(f"Unexpected Spotify API status: {status}")

    async def get_artist(self, artist_id: str) -> Artist:
        """Fetch a single artist by its Spotify identifier.

        Args:
            artist_id: Spotify artist identifier.

        Returns:
            The matching :class:`Artist` entity.

        Raises:
            SpotifyInvalidResponseError: If the payload fails validation.
            SpotifyError: For any Spotify-related failure.
        """
        body = await self._authorized_get(f"/artists/{artist_id}", {})
        try:
            payload = _ArtistPayload.model_validate(body)
        except ValidationError as exc:
            raise SpotifyInvalidResponseError(
                "Invalid artist payload from Spotify"
            ) from exc
        return _artist_from_payload(payload)

    async def get_top_tracks(
        self, artist_id: str, market: str = "MX"
    ) -> list[Track]:
        """Fetch an artist's top tracks for a given market.

        Args:
            artist_id: Spotify artist identifier.
            market: ISO 3166-1 alpha-2 country code.

        Returns:
            A list of :class:`Track` entities.

        Raises:
            SpotifyInvalidResponseError: If the payload fails validation.
            SpotifyError: For any Spotify-related failure.
        """
        body = await self._authorized_get(
            f"/artists/{artist_id}/top-tracks", {"market": market}
        )
        try:
            payload = _TopTracksResponse.model_validate(body)
        except ValidationError as exc:
            raise SpotifyInvalidResponseError(
                "Invalid top-tracks payload from Spotify"
            ) from exc
        return [_track_from_payload(track) for track in payload.tracks]
