"""FastAPI application entry point.

Wires together routers, middleware, error handling and (lazily) the
infrastructure composition root. Run with:

    uvicorn app.presentation.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.infrastructure.config.settings import get_settings
from app.presentation.api.v1 import api_router
from app.presentation.api.v1.routes.health import router as health_router
from app.presentation.middleware.cors import configure_cors
from app.presentation.middleware.error_handler import register_exception_handlers

logger = logging.getLogger(__name__)

APP_TITLE = "Diferenzzia API"
APP_DESCRIPTION = (
    "REST API for the Diferenzzia website."
)
APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan handler.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to FastAPI while the app is running.
    """
    settings = get_settings()
    logger.info(
        "Starting %s v%s (cache TTL: %sh, origins: %s)",
        APP_TITLE,
        APP_VERSION,
        settings.cache_ttl_hours,
        settings.allowed_origins_list,
    )
    yield
    logger.info("Shutting down %s", APP_TITLE)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Returns:
        The fully configured :class:`FastAPI` instance.
    """
    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        lifespan=lifespan,
    )

    settings = get_settings()
    configure_cors(app, settings)
    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router)

    return app


app = create_app()
