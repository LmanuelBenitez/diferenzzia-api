"""Infrastructure external clients package.

Exposes the concrete Spotify authentication helper and API client.
"""

from app.infrastructure.external.spotify_auth import SpotifyAuth
from app.infrastructure.external.spotify_client import SpotifyClient

__all__ = ["SpotifyAuth", "SpotifyClient"]
