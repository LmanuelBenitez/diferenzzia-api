"""Composition root and FastAPI dependency providers.

This module is the single place where infrastructure implementations are
instantiated and injected into the presentation layer. It acts as the
composition root of the clean-architecture graph: routers depend only on
this module (and on application interfaces), never on concrete
infrastructure classes directly.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.application.interfaces.cache_repository import CacheRepository
from app.infrastructure.cache.in_memory_cache import InMemoryCache
from app.infrastructure.config.settings import Settings, get_settings

SECONDS_PER_HOUR = 3600


@lru_cache(maxsize=1)
def _get_cache_singleton() -> InMemoryCache:
    """Return the process-wide in-memory cache singleton.

    Returns:
        The shared :class:`InMemoryCache` instance.
    """
    settings = get_settings()
    return InMemoryCache(ttl_seconds=settings.cache_ttl_hours * SECONDS_PER_HOUR)


def get_cache_repository() -> CacheRepository:
    """Provide the cache repository port.

    Returns:
        A :class:`CacheRepository` implementation.
    """
    return _get_cache_singleton()


async def verify_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """Validate the ``X-API-Key`` header against the configured API key.

    Args:
        x_api_key: Value sent in the ``X-API-Key`` header, if any.

    Raises:
        HTTPException: 401 if the header is missing or does not match.
    """
    settings = get_settings()
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


SettingsDep = Annotated[Settings, Depends(get_settings)]
CacheRepositoryDep = Annotated[CacheRepository, Depends(get_cache_repository)]
ApiKeyDep = Annotated[None, Depends(verify_api_key)]
