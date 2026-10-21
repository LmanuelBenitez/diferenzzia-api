"""Use case: get the artist's top tracks with caching.

Orchestrates the :class:`SpotifyRepository` and the :class:`CacheRepository`
to return the artist's top tracks, hitting the cache when possible and the
Spotify API only when the cache is empty or expired.
"""

from datetime import datetime, timezone

from app.application.dto.track_dto import TrackDTO, track_to_dto
from app.application.interfaces.cache_repository import CacheRepository
from app.application.interfaces.spotify_repository import SpotifyRepository

CACHE_KEY = "spotify:top_tracks"


class GetTopTracksUseCase:
    """Return the artist's top tracks, using the cache when available."""

    def __init__(
        self,
        spotify_repository: SpotifyRepository,
        cache_repository: CacheRepository,
        artist_id: str,
        market: str = "MX",
    ) -> None:
        """Initialize the use case.

        Args:
            spotify_repository: Port used to fetch data from Spotify.
            cache_repository: Port used to cache the results.
            artist_id: Spotify artist identifier to query.
            market: ISO 3166-1 alpha-2 country code for the market.
        """
        self._spotify_repository = spotify_repository
        self._cache_repository = cache_repository
        self._artist_id = artist_id
        self._market = market

    async def execute(self) -> tuple[list[TrackDTO], datetime]:
        """Return top tracks and the timestamp they were last refreshed.

        The result is cached as a ``(tracks, updated_at)`` tuple. When the
        cache is valid the cached data is returned immediately; otherwise
        Spotify is queried and the cache is repopulated.

        Returns:
            A tuple of ``(tracks, updated_at)`` where ``tracks`` is the list
            of :class:`TrackDTO` and ``updated_at`` is the UTC timestamp of
            the last refresh.
        """
        cached = self._cache_repository.get(CACHE_KEY)
        if isinstance(cached, tuple) and len(cached) == 2:
            tracks, updated_at = cached
            if isinstance(tracks, list) and isinstance(updated_at, datetime):
                return tracks, updated_at

        tracks_dto = await self._fetch_from_spotify()
        updated_at = datetime.now(timezone.utc)
        self._cache_repository.set(CACHE_KEY, (tracks_dto, updated_at))
        return tracks_dto, updated_at

    async def _fetch_from_spotify(self) -> list[TrackDTO]:
        """Fetch top tracks from Spotify and map them to DTOs.

        Returns:
            A list of :class:`TrackDTO`.
        """
        tracks = await self._spotify_repository.get_top_tracks(
            self._artist_id, self._market
        )
        return [track_to_dto(track) for track in tracks]
