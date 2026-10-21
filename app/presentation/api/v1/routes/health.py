"""Health check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response body."""

    status: Literal["ok"] = "ok"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return a basic health check response.

    Returns:
        A :class:`HealthResponse` with ``status`` set to ``"ok"``.
    """
    return HealthResponse(status="ok")
