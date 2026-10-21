"""HTTP schemas package.

Exposes all Pydantic schemas used by the HTTP layer.
"""

from app.presentation.api.v1.schemas.artist_schema import (
    ArtistResponse,
)
from app.presentation.api.v1.schemas.track_schema import (
    AlbumSchema,
    ArtistSchema,
    ExternalUrlsSchema,
    ImageSchema,
    TopTracksResponse,
    TrackSchema,
)

__all__ = [
    "AlbumSchema",
    "ArtistResponse",
    "ArtistSchema",
    "ExternalUrlsSchema",
    "ImageSchema",
    "TopTracksResponse",
    "TrackSchema",
]
