"""HTTP response schemas for artist-related endpoints."""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.artist import Artist


class ArtistExternalUrlsSchema(BaseModel):
    """External URLs for an artist."""

    model_config = ConfigDict(from_attributes=True)

    spotify: str = ""


class ArtistImageSchema(BaseModel):
    """Artist image schema."""

    model_config = ConfigDict(from_attributes=True)

    url: str
    height: int | None = None
    width: int | None = None


class ArtistResponse(BaseModel):
    """Response schema for ``GET /api/v1/spotify/artist``."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    uri: str
    images: list[ArtistImageSchema] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    popularity: int = 0
    followers: int = 0
    external_urls: ArtistExternalUrlsSchema = Field(
        default_factory=ArtistExternalUrlsSchema
    )

    @classmethod
    def from_entity(cls, artist: Artist) -> "ArtistResponse":
        """Build the schema from a domain :class:`Artist` entity.

        Args:
            artist: Source domain entity.

        Returns:
            The corresponding response schema.
        """
        return cls(
            id=artist.id,
            name=artist.name,
            uri=artist.uri,
            images=[
                ArtistImageSchema(
                    url=image.url, height=image.height, width=image.width
                )
                for image in artist.images
            ],
            genres=list(artist.genres),
            popularity=artist.popularity,
            followers=artist.followers,
            external_urls=ArtistExternalUrlsSchema(
                spotify=artist.external_urls.get("spotify", "")
            ),
        )
