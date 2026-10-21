"""Spotify Client Credentials authentication.

Implements the Spotify ``client_credentials`` OAuth flow. The access token is
cached in memory and automatically renewed shortly before it expires. No user
login is involved: this is a pure server-to-server flow.
"""

import base64
import time

import httpx

from app.domain.exceptions.spotify_errors import (
    SpotifyAuthenticationError,
    SpotifyServiceUnavailableError,
)

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS = 60


class SpotifyAuth:
    """Manage Spotify access tokens using Client Credentials Flow."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initialize the auth manager.

        Args:
            client_id: Spotify application client ID.
            client_secret: Spotify application client secret.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._expires_at: float = 0.0

    def _build_basic_auth_header(self) -> str:
        """Build the HTTP Basic authorization header.

        Returns:
            The value for the ``Authorization`` header.
        """
        credentials = f"{self._client_id}:{self._client_secret}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    def _is_token_valid(self) -> bool:
        """Check whether the cached token is still usable.

        Returns:
            ``True`` if a token exists and has not expired (minus the safety
            margin), ``False`` otherwise.
        """
        if self._access_token is None:
            return False
        return time.monotonic() < self._expires_at

    async def get_access_token(self) -> str:
        """Return a valid access token, requesting a new one if needed.

        Returns:
            A valid Spotify access token.

        Raises:
            SpotifyAuthenticationError: If Spotify rejects the credentials.
            SpotifyServiceUnavailableError: If Spotify cannot be reached.
        """
        if self._is_token_valid():
            assert self._access_token is not None
            return self._access_token

        await self._request_new_token()
        assert self._access_token is not None
        return self._access_token

    async def _request_new_token(self) -> None:
        """Request a fresh access token from Spotify and cache it.

        Raises:
            SpotifyAuthenticationError: If Spotify rejects the credentials.
            SpotifyServiceUnavailableError: If Spotify cannot be reached.
        """
        headers = {
            "Authorization": self._build_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    SPOTIFY_TOKEN_URL, headers=headers, data=data
                )
        except httpx.RequestError as exc:
            raise SpotifyServiceUnavailableError(
                "Could not reach Spotify authentication service"
            ) from exc

        if response.status_code in (400, 401):
            raise SpotifyAuthenticationError(
                "Invalid Spotify credentials"
            )
        if response.status_code >= 500:
            raise SpotifyServiceUnavailableError(
                "Spotify authentication service is unavailable"
            )
        if response.status_code != 200:
            raise SpotifyAuthenticationError(
                "Unexpected response from Spotify authentication service"
            )

        try:
            payload = response.json()
            token = payload["access_token"]
            expires_in = int(payload.get("expires_in", 3600))
        except (ValueError, KeyError, TypeError) as exc:
            raise SpotifyAuthenticationError(
                "Malformed token response from Spotify"
            ) from exc

        self._access_token = token
        self._expires_at = (
            time.monotonic() + expires_in - TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
        )

    def invalidate(self) -> None:
        """Drop the cached token, forcing a renewal on the next request."""
        self._access_token = None
        self._expires_at = 0.0
