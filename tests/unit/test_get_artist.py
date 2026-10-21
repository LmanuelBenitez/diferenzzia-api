"""Unit tests for the ``GetArtistUseCase``."""

import asyncio

from app.application.use_cases.get_artist import CACHE_KEY, GetArtistUseCase
from app.domain.entities.artist import Artist


class FakeSpotifyRepository:
    """In-memory fake Spotify repository that counts artist calls."""

    def __init__(self, artist: Artist) -> None:
        """Initialize the fake.

        Args:
            artist: The artist to return.
        """
        self._artist = artist
        self.artist_calls = 0

    async def get_artist(self, artist_id: str) -> Artist:
        """Return the configured artist and count the call."""
        self.artist_calls += 1
        return self._artist

    async def get_top_tracks(self, artist_id: str, market: str = "MX") -> list:
        """Not used in these tests."""
        raise NotImplementedError


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
        genres=["rock"],
        popularity=42,
        followers=1234,
    )


def test_execute_fetches_from_spotify_on_cache_miss() -> None:
    """On a cold cache, Spotify is queried once."""
    repository = FakeSpotifyRepository(_build_artist())
    cache = FakeCacheRepository()
    use_case = GetArtistUseCase(repository, cache, artist_id="a1")

    artist = asyncio.run(use_case.execute())

    assert artist.id == "a1"
    assert repository.artist_calls == 1


def test_execute_uses_cache_on_hit() -> None:
    """On a warm cache, Spotify is not queried again."""
    repository = FakeSpotifyRepository(_build_artist())
    cache = FakeCacheRepository()
    use_case = GetArtistUseCase(repository, cache, artist_id="a1")

    first = asyncio.run(use_case.execute())
    second = asyncio.run(use_case.execute())

    assert repository.artist_calls == 1
    assert first == second


def test_execute_ignores_unexpected_cache_type() -> None:
    """A cache entry that is not an Artist must be ignored."""
    repository = FakeSpotifyRepository(_build_artist())
    cache = FakeCacheRepository()
    cache.set(CACHE_KEY, {"not": "an artist"})
    use_case = GetArtistUseCase(repository, cache, artist_id="a1")

    artist = asyncio.run(use_case.execute())

    assert artist.id == "a1"
    assert repository.artist_calls == 1
