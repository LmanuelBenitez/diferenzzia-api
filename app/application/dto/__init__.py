"""Application DTO package.

Exposes the Data Transfer Objects and the mapping helpers used to convert
domain entities into transport-friendly structures.
"""

from app.application.dto.track_dto import (
    AlbumDTO,
    ArtistDTO,
    ExternalUrlsDTO,
    ImageDTO,
    TrackDTO,
    album_to_dto,
    track_to_dto,
)

__all__ = [
    "AlbumDTO",
    "ArtistDTO",
    "ExternalUrlsDTO",
    "ImageDTO",
    "TrackDTO",
    "album_to_dto",
    "track_to_dto",
]
