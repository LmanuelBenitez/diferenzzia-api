"""Global error handlers for the FastAPI application.

Translates unhandled exceptions into safe HTTP responses. Internal details
are never leaked: clients receive generic, safe messages and the original
error is logged server-side.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

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
    """Register the generic exception handler on the app.

    Args:
        app: The FastAPI application instance.
    """
    app.add_exception_handler(Exception, _handle_unexpected)
