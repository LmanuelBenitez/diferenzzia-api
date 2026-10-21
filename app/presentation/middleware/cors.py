"""CORS configuration for the FastAPI application.

The allowed origins are read from the ``ALLOWED_ORIGINS`` environment
variable (comma-separated) via the settings module.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config.settings import Settings


ALLOWED_METHODS = ["GET", "POST", "OPTIONS"]
ALLOWED_HEADERS = ["Content-Type", "X-API-Key"]


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Attach the CORS middleware to the FastAPI application.

    Args:
        app: The FastAPI application instance.
        settings: Loaded application settings.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=False,
        allow_methods=ALLOWED_METHODS,
        allow_headers=ALLOWED_HEADERS,
    )
