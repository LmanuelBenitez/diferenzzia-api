"""Global error handlers for the FastAPI application.

Translates domain exceptions into HTTP responses. Internal details from
Spotify are never leaked: clients receive generic, safe messages and the
original error is logged server-side.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions.spotify_errors import (
    SpotifyAuthenticationError,
    SpotifyError,
    SpotifyInvalidResponseError,
    SpotifyNotFoundError,
    SpotifyRateLimitError,
    SpotifyServiceUnavailableError,
)

logger = logging.getLogger(__name__)


def _json_error(status_code: int, detail: str) -> JSONResponse:
    """Build a consistent JSON error response.

    Args:
        status_code: HTTP status code.
        detail: Safe, generic error message for the client.

    Returns:
        A :class:`JSONResponse` with the given status and body.
    """
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def _handle_not_found(
    request: Request, exc: SpotifyNotFoundError
) -> JSONResponse:
    """Handle missing Spotify resources.

    Args:
        request: Incoming request (unused, kept for signature compatibility).
        exc: The raised domain exception.

    Returns:
        A 404 JSON response.
    """
    logger.warning("Spotify resource not found: %s", exc.message)
    return _json_error(
        status.HTTP_404_NOT_FOUND, "The requested resource was not found"
    )


async def _handle_auth(
    request: Request, exc: SpotifyAuthenticationError
) -> JSONResponse:
    """Handle Spotify authentication failures.

    Args:
        request: Incoming request (unused).
        exc: The raised domain exception.

    Returns:
        A 502 JSON response.
    """
    logger.error("Spotify authentication failed: %s", exc.message)
    return _json_error(
        status.HTTP_502_BAD_GATEWAY,
        "The music service is temporarily unavailable",
    )


async def _handle_rate_limit(
    request: Request, exc: SpotifyRateLimitError
) -> JSONResponse:
    """Handle Spotify rate limiting.

    Args:
        request: Incoming request (unused).
        exc: The raised domain exception.

    Returns:
        A 503 JSON response.
    """
    logger.warning("Spotify rate limit reached: %s", exc.message)
    return _json_error(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "The music service is rate-limited, please try again later",
    )


async def _handle_unavailable(
    request: Request, exc: SpotifyServiceUnavailableError
) -> JSONResponse:
    """Handle Spotify 5xx / network errors.

    Args:
        request: Incoming request (unused).
        exc: The raised domain exception.

    Returns:
        A 503 JSON response.
    """
    logger.error("Spotify service unavailable: %s", exc.message)
    return _json_error(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "The music service is temporarily unavailable",
    )


async def _handle_invalid_response(
    request: Request, exc: SpotifyInvalidResponseError
) -> JSONResponse:
    """Handle malformed Spotify payloads.

    Args:
        request: Incoming request (unused).
        exc: The raised domain exception.

    Returns:
        A 502 JSON response.
    """
    logger.error("Invalid Spotify response: %s", exc.message)
    return _json_error(
        status.HTTP_502_BAD_GATEWAY,
        "Unexpected response from the music service",
    )


async def _handle_generic_spotify(
    request: Request, exc: SpotifyError
) -> JSONResponse:
    """Handle any other Spotify domain error.

    Args:
        request: Incoming request (unused).
        exc: The raised domain exception.

    Returns:
        A 502 JSON response.
    """
    logger.error("Spotify error: %s", exc.message)
    return _json_error(
        status.HTTP_502_BAD_GATEWAY,
        "The music service could not be reached",
    )


async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unexpected, unhandled exception.

    Args:
        request: Incoming request.
        exc: The raised exception.

    Returns:
        A 500 JSON response.
    """
    logger.exception(
        "Unhandled error while processing %s %s", request.method, request.url.path
    )
    return _json_error(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "An unexpected error occurred",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all domain and generic exception handlers on the app.

    Args:
        app: The FastAPI application instance.
    """
    app.add_exception_handler(SpotifyNotFoundError, _handle_not_found)  # type: ignore[arg-type]
    app.add_exception_handler(SpotifyAuthenticationError, _handle_auth)  # type: ignore[arg-type]
    app.add_exception_handler(SpotifyRateLimitError, _handle_rate_limit)  # type: ignore[arg-type]
    app.add_exception_handler(
        SpotifyServiceUnavailableError, _handle_unavailable  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        SpotifyInvalidResponseError, _handle_invalid_response  # type: ignore[arg-type]
    )
    app.add_exception_handler(SpotifyError, _handle_generic_spotify)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_unexpected)
