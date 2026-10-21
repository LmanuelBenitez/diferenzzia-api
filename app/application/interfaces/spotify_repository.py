"""Spotify repository port.

Defines the abstract contract for fetching data from Spotify. The
application layer only knows about this Protocol; the concrete
``SpotifyClient`` implementation lives in the infrastructure layer.
"""

from typing import Protocol, runtime_checkable

from app.domain.entities.artist import Artist
from app.domain.entities.track import Track


@runtime_checkable
class SpotifyRepository(Protocol):
    """Abstract source of Spotify data."""

    async def get_artist(self, artist_id: str) -> Artist:
        """Fetch a single artist by its Spotify identifier.

        Args:
            artist_id: Spotify artist identifier.

        Returns:
            The matching :class:`Artist` entity.

        Raises:
            SpotifyNotFoundError: If the artist does not exist.
            SpotifyError: For any other Spotify-related failure.
        """
        ...

    async def get_top_tracks(
        self, artist_id: str, market: str = "MX"
    ) -> list[Track]:
        """Fetch an artist's top tracks for a given market.

        Args:
            artist_id: Spotify artist identifier.
            market: ISO 3166-1 alpha-2 country code (e.g. ``"MX"``).

        Returns:
            A list of :class:`Track` entities ordered by popularity.

        Raises:
            SpotifyNotFoundError: If the artist does not exist.
            SpotifyError: For any other Spotify-related failure.
        """
        ...
