"""Domain exceptions package.

Exposes domain-level exceptions. These are framework-agnostic and are
mapped to HTTP responses in the presentation layer.
"""

from app.domain.exceptions.spotify_errors import (
    SpotifyAuthenticationError,
    SpotifyError,
    SpotifyInvalidResponseError,
    SpotifyNotFoundError,
    SpotifyRateLimitError,
    SpotifyServiceUnavailableError,
)

__all__ = [
    "SpotifyAuthenticationError",
    "SpotifyError",
    "SpotifyInvalidResponseError",
    "SpotifyNotFoundError",
    "SpotifyRateLimitError",
    "SpotifyServiceUnavailableError",
]
