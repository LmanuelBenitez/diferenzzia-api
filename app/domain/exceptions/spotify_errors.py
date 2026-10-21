"""Domain exceptions related to the Spotify integration.

These exceptions belong to the domain layer and must not depend on any
third-party library (no httpx, no FastAPI). Infrastructure is responsible
for translating low-level errors into these domain errors.
"""


class SpotifyError(Exception):
    """Base class for all Spotify-related domain errors."""

    def __init__(self, message: str = "Spotify service error") -> None:
        """Initialize the error.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)
        self.message = message


class SpotifyAuthenticationError(SpotifyError):
    """Raised when authentication with Spotify fails (invalid credentials)."""

    def __init__(self, message: str = "Spotify authentication failed") -> None:
        """Initialize the error.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)


class SpotifyRateLimitError(SpotifyError):
    """Raised when Spotify returns a 429 Too Many Requests response."""

    def __init__(self, message: str = "Spotify rate limit exceeded") -> None:
        """Initialize the error.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)


class SpotifyNotFoundError(SpotifyError):
    """Raised when a requested Spotify resource does not exist (404)."""

    def __init__(self, message: str = "Spotify resource not found") -> None:
        """Initialize the error.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)


class SpotifyServiceUnavailableError(SpotifyError):
    """Raised when Spotify is unreachable or returns a 5xx error."""

    def __init__(self, message: str = "Spotify service is unavailable") -> None:
        """Initialize the error.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)


class SpotifyInvalidResponseError(SpotifyError):
    """Raised when Spotify returns a payload that cannot be validated."""

    def __init__(self, message: str = "Invalid response received from Spotify") -> None:
        """Initialize the error.

        Args:
            message: Human-readable description of the error.
        """
        super().__init__(message)
