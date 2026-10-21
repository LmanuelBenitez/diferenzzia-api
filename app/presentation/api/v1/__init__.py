"""API v1 router aggregator."""

from fastapi import APIRouter

from app.presentation.api.v1.routes import spotify

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(spotify.router)

__all__ = ["api_router"]
