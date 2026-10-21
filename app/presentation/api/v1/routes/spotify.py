"""Spotify-related HTTP routes.

Exposes the endpoints consumed by the React frontend. Routers depend only
on application use cases (injected via FastAPI ``Depends``), never on
infrastructure directly.
"""

from fastapi import APIRouter, status

from app.presentation.api.v1.schemas.artist_schema import ArtistResponse
from app.presentation.api.v1.schemas.track_schema import (
    TopTracksResponse,
    TrackSchema,
)
from app.presentation.dependencies import (
    ApiKeyDep,
    ArtistUseCaseDep,
    CacheRepositoryDep,
    TopTracksUseCaseDep,
)

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/top-tracks", response_model=TopTracksResponse)
async def get_top_tracks(
    use_case: TopTracksUseCaseDep,
) -> TopTracksResponse:
    """Return the artist's top tracks.

    The result is served from an in-memory cache when valid; otherwise it is
    fetched from Spotify and the cache is refreshed.

    Args:
        use_case: Injected ``GetTopTracksUseCase``.

    Returns:
        A :class:`TopTracksResponse` with tracks and the refresh timestamp.
    """
    tracks_dto, updated_at = await use_case.execute()
    return TopTracksResponse(
        tracks=[TrackSchema.from_dto(track) for track in tracks_dto],
        updated_at=updated_at,
    )


@router.get("/artist", response_model=ArtistResponse)
async def get_artist(
    use_case: ArtistUseCaseDep,
) -> ArtistResponse:
    """Return the configured artist's profile.

    Args:
        use_case: Injected ``GetArtistUseCase``.

    Returns:
        An :class:`ArtistResponse` with the artist data.
    """
    artist = await use_case.execute()
    return ArtistResponse.from_entity(artist)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_cache(
    _: ApiKeyDep,
    cache: CacheRepositoryDep,
) -> dict[str, str]:
    """Force the cache to be cleared, so the next request refetches Spotify.

    Args:
        _: API key guard (validated via the ``X-API-Key`` header).
        cache: Injected cache repository port.

    Returns:
        A small JSON confirmation payload.
    """
    cache.clear()
    return {"status": "cache cleared"}
