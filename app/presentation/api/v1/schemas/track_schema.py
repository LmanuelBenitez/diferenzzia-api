"""HTTP response schemas for track-related endpoints.

These schemas define the exact JSON contract consumed by the React frontend.
Field names are snake_case and the shape mirrors the Spotify track object,
because the frontend already has matching TypeScript types. DO NOT change
field names or structure without coordinating with the frontend.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.track_dto import (
    AlbumDTO,
    ArtistDTO,
    ExternalUrlsDTO,
    ImageDTO,
    TrackDTO,
)


class ExternalUrlsSchema(BaseModel):
    """External URLs response schema."""

    model_config = ConfigDict(from_attributes=True)

    spotify: str = ""

    @classmethod
    def from_dto(cls, dto: ExternalUrlsDTO) -> "ExternalUrlsSchema":
        """Build the schema from a DTO.

        Args:
            dto: Source DTO.

        Returns:
            The corresponding schema instance.
        """
        return cls(spotify=dto.spotify)


class ImageSchema(BaseModel):
    """Image response schema."""

    model_config = ConfigDict(from_attributes=True)

    url: str
    height: int | None = None
    width: int | None = None

    @classmethod
    def from_dto(cls, dto: ImageDTO) -> "ImageSchema":
        """Build the schema from a DTO.

        Args:
            dto: Source DTO.

        Returns:
            The corresponding schema instance.
        """
        return cls(url=dto.url, height=dto.height, width=dto.width)


class ArtistSchema(BaseModel):
    """Artist response schema (nested in albums and tracks)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    uri: str
    external_urls: ExternalUrlsSchema = Field(
        default_factory=ExternalUrlsSchema
    )

    @classmethod
    def from_dto(cls, dto: ArtistDTO) -> "ArtistSchema":
        """Build the schema from a DTO.

        Args:
            dto: Source DTO.

        Returns:
            The corresponding schema instance.
        """
        return cls(
            id=dto.id,
            name=dto.name,
            uri=dto.uri,
            external_urls=ExternalUrlsSchema.from_dto(dto.external_urls),
        )


class AlbumSchema(BaseModel):
    """Album response schema (nested in tracks)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    album_type: str
    total_tracks: int
    images: list[ImageSchema] = Field(default_factory=list)
    release_date: str = ""
    artists: list[ArtistSchema] = Field(default_factory=list)
    external_urls: ExternalUrlsSchema = Field(
        default_factory=ExternalUrlsSchema
    )

    @classmethod
    def from_dto(cls, dto: AlbumDTO) -> "AlbumSchema":
        """Build the schema from a DTO.

        Args:
            dto: Source DTO.

        Returns:
            The corresponding schema instance.
        """
        return cls(
            id=dto.id,
            name=dto.name,
            album_type=dto.album_type,
            total_tracks=dto.total_tracks,
            images=[ImageSchema.from_dto(image) for image in dto.images],
            release_date=dto.release_date,
            artists=[ArtistSchema.from_dto(artist) for artist in dto.artists],
            external_urls=ExternalUrlsSchema.from_dto(dto.external_urls),
        )


class TrackSchema(BaseModel):
    """Track response schema mirroring the Spotify track object."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    duration_ms: int
    popularity: int
    preview_url: str | None = None
    explicit: bool
    track_number: int
    disc_number: int
    album: AlbumSchema
    artists: list[ArtistSchema] = Field(default_factory=list)
    external_urls: ExternalUrlsSchema = Field(
        default_factory=ExternalUrlsSchema
    )

    @classmethod
    def from_dto(cls, dto: TrackDTO) -> "TrackSchema":
        """Build the schema from a DTO.

        Args:
            dto: Source DTO.

        Returns:
            The corresponding schema instance.
        """
        return cls(
            id=dto.id,
            name=dto.name,
            duration_ms=dto.duration_ms,
            popularity=dto.popularity,
            preview_url=dto.preview_url,
            explicit=dto.explicit,
            track_number=dto.track_number,
            disc_number=dto.disc_number,
            album=AlbumSchema.from_dto(dto.album),
            artists=[ArtistSchema.from_dto(artist) for artist in dto.artists],
            external_urls=ExternalUrlsSchema.from_dto(dto.external_urls),
        )


class TopTracksResponse(BaseModel):
    """Response envelope for ``GET /api/v1/spotify/top-tracks``."""

    tracks: list[TrackSchema] = Field(default_factory=list)
    updated_at: datetime
