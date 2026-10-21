"""Use case: get the artist's profile with caching.

Orchestrates the :class:`SpotifyRepository` and the :class:`CacheRepository`
to return the artist profile, hitting the cache when possible and Spotify
only when the cache is empty or expired.
"""

from app.application.interfaces.cache_repository import CacheRepository
from app.application.interfaces.spotify_repository import SpotifyRepository
from app.domain.entities.artist import Artist

CACHE_KEY = "spotify:artist"


class GetArtistUseCase:
    """Return the artist profile, using the cache when available."""

    def __init__(
        self,
        spotify_repository: SpotifyRepository,
        cache_repository: CacheRepository,
        artist_id: str,
    ) -> None:
        """Initialize the use case.

        Args:
            spotify_repository: Port used to fetch data from Spotify.
            cache_repository: Port used to cache the results.
            artist_id: Spotify artist identifier to query.
        """
        self._spotify_repository = spotify_repository
        self._cache_repository = cache_repository
        self._artist_id = artist_id

    async def execute(self) -> Artist:
        """Return the artist profile, fetching from Spotify if needed.

        Returns:
            The :class:`Artist` domain entity.
        """
        cached = self._cache_repository.get(CACHE_KEY)
        if isinstance(cached, Artist):
            return cached

        artist = await self._spotify_repository.get_artist(self._artist_id)
        self._cache_repository.set(CACHE_KEY, artist)
        return artist
