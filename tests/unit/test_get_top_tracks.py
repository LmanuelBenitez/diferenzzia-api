"""Unit tests for the ``GetTopTracksUseCase``.

These tests use fake implementations of the ports, so no network access or
concrete infrastructure is required. Async use cases are driven with
``asyncio.run`` to avoid depending on any pytest async plugin.
"""

import asyncio
from datetime import datetime

from app.application.use_cases.get_top_tracks import (
    CACHE_KEY,
    GetTopTracksUseCase,
)
from app.domain.entities.album import Album
from app.domain.entities.artist import Artist
from app.domain.entities.track import Track


class FakeSpotifyRepository:
    """In-memory fake Spotify repository that counts calls."""

    def __init__(self, tracks: list[Track]) -> None:
        """Initialize the fake.

        Args:
            tracks: Tracks to return from ``get_top_tracks``.
        """
        self._tracks = tracks
        self.top_tracks_calls = 0

    async def get_artist(self, artist_id: str) -> Artist:
        """Not used in these tests."""
        raise NotImplementedError

    async def get_top_tracks(
        self, artist_id: str, market: str = "MX"
    ) -> list[Track]:
        """Return the configured tracks and count the call."""
        self.top_tracks_calls += 1
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


def _build_track(track_id: str = "t1") -> Track:
    """Build a valid :class:`Track` for testing.

    Args:
        track_id: Identifier for the track.

    Returns:
        A fully populated track entity.
    """
    artist = Artist(
        id="a1",
        name="Diferenzzia",
        uri="spotify:artist:a1",
        external_urls={"spotify": "https://open.spotify.com/artist/a1"},
    )
    album = Album(
        id="al1",
        name="Album",
        album_type="album",
        total_tracks=10,
        release_date="2024-01-01",
        artists=[artist],
        external_urls={"spotify": "https://open.spotify.com/album/al1"},
    )
    return Track(
        id=track_id,
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


def test_execute_fetches_from_spotify_on_cache_miss() -> None:
    """On a cold cache, the use case must call Spotify once."""
    repository = FakeSpotifyRepository([_build_track()])
    cache = FakeCacheRepository()
    use_case = GetTopTracksUseCase(repository, cache, artist_id="a1")

    tracks, updated_at = asyncio.run(use_case.execute())

    assert len(tracks) == 1
    assert tracks[0].id == "t1"
    assert repository.top_tracks_calls == 1
    assert isinstance(updated_at, datetime)
    assert updated_at.tzinfo is not None


def test_execute_uses_cache_on_hit() -> None:
    """On a warm cache, Spotify must not be called again."""
    repository = FakeSpotifyRepository([_build_track()])
    cache = FakeCacheRepository()
    use_case = GetTopTracksUseCase(repository, cache, artist_id="a1")

    first_tracks, first_updated = asyncio.run(use_case.execute())
    second_tracks, second_updated = asyncio.run(use_case.execute())

    assert repository.top_tracks_calls == 1
    assert first_tracks == second_tracks
    assert first_updated == second_updated


def test_execute_ignores_non_tuple_cache_value() -> None:
    """A malformed cache value must be ignored and refetched."""
    repository = FakeSpotifyRepository([_build_track()])
    cache = FakeCacheRepository()
    cache.set(CACHE_KEY, "garbage")
    use_case = GetTopTracksUseCase(repository, cache, artist_id="a1")

    tracks, _ = asyncio.run(use_case.execute())

    assert len(tracks) == 1
    assert repository.top_tracks_calls == 1


def test_execute_returns_track_dto_shape() -> None:
    """The DTO must expose the fields the HTTP contract depends on."""
    repository = FakeSpotifyRepository([_build_track()])
    cache = FakeCacheRepository()
    use_case = GetTopTracksUseCase(repository, cache, artist_id="a1")

    tracks, _ = asyncio.run(use_case.execute())
    dto = tracks[0]

    assert dto.id == "t1"
    assert dto.album.id == "al1"
    assert dto.artists[0].name == "Diferenzzia"
    assert dto.external_urls.spotify.endswith("/track/t1")
