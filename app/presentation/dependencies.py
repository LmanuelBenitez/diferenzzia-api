"""Composition root and FastAPI dependency providers.

This module is the single place where infrastructure implementations are
instantiated and injected into application use cases. It acts as the
composition root of the clean-architecture graph: routers depend only on
this module (and on application interfaces), never on concrete
infrastructure classes directly.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.application.interfaces.cache_repository import CacheRepository
from app.application.interfaces.spotify_repository import SpotifyRepository
from app.application.use_cases.get_artist import GetArtistUseCase
from app.application.use_cases.get_top_tracks import GetTopTracksUseCase
from app.infrastructure.cache.in_memory_cache import InMemoryCache
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.external.spotify_auth import SpotifyAuth
from app.infrastructure.external.spotify_client import SpotifyClient

SECONDS_PER_HOUR = 3600
DEFAULT_MARKET = "MX"


@lru_cache(maxsize=1)
def _get_cache_singleton() -> InMemoryCache:
    """Return the process-wide in-memory cache singleton.

    Returns:
        The shared :class:`InMemoryCache` instance.
    """
    settings = get_settings()
    return InMemoryCache(ttl_seconds=settings.cache_ttl_hours * SECONDS_PER_HOUR)


@lru_cache(maxsize=1)
def _get_spotify_repository_singleton() -> SpotifyClient:
    """Return the process-wide Spotify client singleton.

    Returns:
        The shared :class:`SpotifyClient` instance.
    """
    settings = get_settings()
    auth = SpotifyAuth(
        client_id=settings.spotify_client_id,
        client_secret=settings.spotify_client_secret,
    )
    return SpotifyClient(auth=auth)


def get_cache_repository() -> CacheRepository:
    """Provide the cache repository port.

    Returns:
        A :class:`CacheRepository` implementation.
    """
    return _get_cache_singleton()


def get_spotify_repository() -> SpotifyRepository:
    """Provide the Spotify repository port.

    Returns:
        A :class:`SpotifyRepository` implementation.
    """
    return _get_spotify_repository_singleton()


def get_top_tracks_use_case(
    spotify_repository: Annotated[
        SpotifyRepository, Depends(get_spotify_repository)
    ],
    cache_repository: Annotated[
        CacheRepository, Depends(get_cache_repository)
    ],
) -> GetTopTracksUseCase:
    """Build the ``GetTopTracksUseCase`` with injected dependencies.

    Args:
        spotify_repository: Injected Spotify repository port.
        cache_repository: Injected cache repository port.

    Returns:
        A configured :class:`GetTopTracksUseCase` instance.
    """
    settings = get_settings()
    return GetTopTracksUseCase(
        spotify_repository=spotify_repository,
        cache_repository=cache_repository,
        artist_id=settings.spotify_artist_id,
        market=DEFAULT_MARKET,
    )


def get_artist_use_case(
    spotify_repository: Annotated[
        SpotifyRepository, Depends(get_spotify_repository)
    ],
    cache_repository: Annotated[
        CacheRepository, Depends(get_cache_repository)
    ],
) -> GetArtistUseCase:
    """Build the ``GetArtistUseCase`` with injected dependencies.

    Args:
        spotify_repository: Injected Spotify repository port.
        cache_repository: Injected cache repository port.

    Returns:
        A configured :class:`GetArtistUseCase` instance.
    """
    settings = get_settings()
    return GetArtistUseCase(
        spotify_repository=spotify_repository,
        cache_repository=cache_repository,
        artist_id=settings.spotify_artist_id,
    )


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
TopTracksUseCaseDep = Annotated[GetTopTracksUseCase, Depends(get_top_tracks_use_case)]
ArtistUseCaseDep = Annotated[GetArtistUseCase, Depends(get_artist_use_case)]
CacheRepositoryDep = Annotated[CacheRepository, Depends(get_cache_repository)]
ApiKeyDep = Annotated[None, Depends(verify_api_key)]
