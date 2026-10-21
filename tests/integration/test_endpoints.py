"""Integration tests for the HTTP endpoints.

The app is exercised through FastAPI's ``TestClient``. Dependencies that
would touch Spotify or the network are overridden with fakes, so these
tests are hermetic.
"""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.application.use_cases.get_artist import GetArtistUseCase
from app.application.use_cases.get_top_tracks import GetTopTracksUseCase
from app.domain.entities.album import Album
from app.domain.entities.artist import Artist
from app.domain.entities.image import Image
from app.domain.entities.track import Track
from app.presentation.dependencies import (
    get_artist_use_case,
    get_top_tracks_use_case,
)
from app.presentation.main import app


class FakeSpotifyRepository:
    """Fake Spotify repository returning fixed entities."""

    def __init__(self, artist: Artist, tracks: list[Track]) -> None:
        """Initialize the fake.

        Args:
            artist: Artist to return.
            tracks: Tracks to return.
        """
        self._artist = artist
        self._tracks = tracks

    async def get_artist(self, artist_id: str) -> Artist:
        """Return the configured artist."""
        return self._artist

    async def get_top_tracks(
        self, artist_id: str, market: str = "MX"
    ) -> list[Track]:
        """Return the configured tracks."""
        return self._tracks


class FakeCacheRepository:
    """Simple dict-backed fake cache."""

    def __init__(self) -> None:
        """Initialize the empty store."""
        self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        """Return a stored value if any."""
        return self._store.get(key)

    def set(self, key: str, value: object) -> None:
        """Store a value."""
        self._store[key] = value

    def delete(self, key: str) -> None:
        """Remove a value."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear the store."""
        self._store.clear()


def _build_artist() -> Artist:
    """Build a valid :class:`Artist` for testing.

    Returns:
        A fully populated artist entity.
    """
    return Artist(
        id="a1",
        name="Diferenzzia",
        uri="spotify:artist:a1",
        external_urls={"spotify": "https://open.spotify.com/artist/a1"},
        images=[Image(url="https://img/1.jpg", height=640, width=640)],
        genres=["rock"],
        popularity=42,
        followers=1234,
    )


def _build_track() -> Track:
    """Build a valid :class:`Track` for testing.

    Returns:
        A fully populated track entity.
    """
    artist = _build_artist()
    album = Album(
        id="al1",
        name="Album",
        album_type="album",
        total_tracks=10,
        images=[Image(url="https://img/al.jpg", height=640, width=640)],
        release_date="2024-01-01",
        artists=[artist],
        external_urls={"spotify": "https://open.spotify.com/album/al1"},
    )
    return Track(
        id="t1",
        name="Song",
        duration_ms=180000,
        popularity=80,
        preview_url=None,
        explicit=False,
        track_number=1,
        disc_number=1,
        album=album,
        artists=[artist],
        external_urls={"spotify": "https://open.spotify.com/track/t1"},
    )


@pytest.fixture
def client() -> TestClient:
    """Provide a ``TestClient`` with fake dependencies injected.

    Returns:
        A ``TestClient`` bound to the FastAPI app.
    """
    repository = FakeSpotifyRepository(_build_artist(), [_build_track()])
    cache = FakeCacheRepository()

    def _top_tracks() -> GetTopTracksUseCase:
        return GetTopTracksUseCase(repository, cache, artist_id="a1")

    def _artist() -> GetArtistUseCase:
        return GetArtistUseCase(repository, cache, artist_id="a1")

    app.dependency_overrides[get_top_tracks_use_case] = _top_tracks
    app.dependency_overrides[get_artist_use_case] = _artist

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_returns_ok(client: TestClient) -> None:
    """``GET /health`` returns ``{"status": "ok"}``."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_top_tracks_returns_expected_contract(client: TestClient) -> None:
    """``GET /top-tracks`` returns the exact frontend contract."""
    response = client.get("/api/v1/spotify/top-tracks")
    assert response.status_code == 200

    body = response.json()
    assert set(body.keys()) == {"tracks", "updated_at"}
    assert len(body["tracks"]) == 1

    track = body["tracks"][0]
    for field in (
        "id",
        "name",
        "duration_ms",
        "popularity",
        "preview_url",
        "explicit",
        "track_number",
        "disc_number",
        "album",
        "artists",
        "external_urls",
    ):
        assert field in track

    album = track["album"]
    for field in (
        "id",
        "name",
        "album_type",
        "total_tracks",
        "images",
        "release_date",
        "artists",
        "external_urls",
    ):
        assert field in album

    datetime.fromisoformat(body["updated_at"])


def test_artist_returns_expected_contract(client: TestClient) -> None:
    """``GET /artist`` returns the artist profile contract."""
    response = client.get("/api/v1/spotify/artist")
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == "a1"
    assert body["name"] == "Diferenzzia"
    assert body["followers"] == 1234
    assert body["genres"] == ["rock"]


def test_refresh_requires_api_key(client: TestClient) -> None:
    """``POST /refresh`` without the API key returns 401."""
    response = client.post("/api/v1/spotify/refresh")
    assert response.status_code == 401
