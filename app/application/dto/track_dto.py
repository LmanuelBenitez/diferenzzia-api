"""Data Transfer Objects for track data.

DTOs decouple the application/presentation layers from domain entities and
from the raw Spotify payloads. They are plain dataclasses with no external
dependencies.
"""

from dataclasses import dataclass, field

from app.domain.entities.album import Album as AlbumEntity
from app.domain.entities.artist import Artist
from app.domain.entities.image import Image
from app.domain.entities.track import Track as TrackEntity


@dataclass(frozen=True)
class ExternalUrlsDTO:
    """Mapping of external service name to URL.

    Attributes:
        spotify: Spotify web URL for the resource.
    """

    spotify: str = ""


@dataclass(frozen=True)
class ImageDTO:
    """Image transfer object.

    Attributes:
        url: Public URL of the image.
        height: Image height in pixels, if known.
        width: Image width in pixels, if known.
    """

    url: str
    height: int | None = None
    width: int | None = None

    @classmethod
    def from_entity(cls, image: Image) -> "ImageDTO":
        """Build a DTO from a domain :class:`Image` entity.

        Args:
            image: Source domain entity.

        Returns:
            The corresponding DTO.
        """
        return cls(url=image.url, height=image.height, width=image.width)


@dataclass(frozen=True)
class ArtistDTO:
    """Artist transfer object.

    Attributes:
        id: Spotify identifier.
        name: Artist display name.
        uri: Spotify URI.
        external_urls: External URLs mapping.
    """

    id: str
    name: str
    uri: str
    external_urls: ExternalUrlsDTO = field(default_factory=ExternalUrlsDTO)

    @classmethod
    def from_entity(cls, artist: Artist) -> "ArtistDTO":
        """Build a DTO from a domain :class:`Artist` entity.

        Args:
            artist: Source domain entity.

        Returns:
            The corresponding DTO.
        """
        return cls(
            id=artist.id,
            name=artist.name,
            uri=artist.uri,
            external_urls=ExternalUrlsDTO(
                spotify=artist.external_urls.get("spotify", "")
            ),
        )


@dataclass(frozen=True)
class AlbumDTO:
    """Album transfer object.

    Attributes:
        id: Spotify identifier.
        name: Album display name.
        album_type: Album, single or compilation.
        total_tracks: Total number of tracks.
        images: Album cover images.
        release_date: Release date string.
        artists: Album-level artists.
        external_urls: External URLs mapping.
    """

    id: str
    name: str
    album_type: str
    total_tracks: int
    images: list[ImageDTO] = field(default_factory=list)
    release_date: str = ""
    artists: list[ArtistDTO] = field(default_factory=list)
    external_urls: ExternalUrlsDTO = field(default_factory=ExternalUrlsDTO)


@dataclass(frozen=True)
class TrackDTO:
    """Track transfer object mirroring the Spotify track shape.

    Attributes:
        id: Spotify identifier.
        name: Track display name.
        duration_ms: Duration in milliseconds.
        popularity: Popularity score (0-100).
        preview_url: Preview URL or ``None``.
        explicit: Whether the track is explicit.
        track_number: Track position within the disc.
        disc_number: Disc number.
        album: Album the track belongs to.
        artists: Track-level artists.
        external_urls: External URLs mapping.
    """

    id: str
    name: str
    duration_ms: int
    popularity: int
    preview_url: str | None
    explicit: bool
    track_number: int
    disc_number: int
    album: AlbumDTO
    artists: list[ArtistDTO] = field(default_factory=list)
    external_urls: ExternalUrlsDTO = field(default_factory=ExternalUrlsDTO)


def _external_urls_dict(mapping: dict[str, str]) -> ExternalUrlsDTO:
    """Convert a raw external URL mapping into a DTO.

    Args:
        mapping: Raw ``{"spotify": "..."}`` mapping.

    Returns:
        The corresponding :class:`ExternalUrlsDTO`.
    """
    return ExternalUrlsDTO(spotify=mapping.get("spotify", ""))


def _artist_to_dto(artist: Artist) -> ArtistDTO:
    """Map a domain :class:`Artist` entity to an :class:`ArtistDTO`.

    Args:
        artist: Source domain entity.

    Returns:
        The corresponding DTO.
    """
    return ArtistDTO(
        id=artist.id,
        name=artist.name,
        uri=artist.uri,
        external_urls=_external_urls_dict(artist.external_urls),
    )


def album_to_dto(album: "AlbumEntity") -> AlbumDTO:
    """Map a domain album entity to an :class:`AlbumDTO`.

    Args:
        album: Source domain album entity.

    Returns:
        The corresponding DTO.
    """
    return AlbumDTO(
        id=album.id,
        name=album.name,
        album_type=album.album_type,
        total_tracks=album.total_tracks,
        images=[ImageDTO.from_entity(image) for image in album.images],
        release_date=album.release_date,
        artists=[_artist_to_dto(artist) for artist in album.artists],
        external_urls=_external_urls_dict(album.external_urls),
    )


def track_to_dto(track: "TrackEntity") -> TrackDTO:
    """Map a domain track entity to a :class:`TrackDTO`.

    Args:
        track: Source domain track entity.

    Returns:
        The corresponding DTO.
    """
    return TrackDTO(
        id=track.id,
        name=track.name,
        duration_ms=track.duration_ms,
        popularity=track.popularity,
        preview_url=track.preview_url,
        explicit=track.explicit,
        track_number=track.track_number,
        disc_number=track.disc_number,
        album=album_to_dto(track.album),
        artists=[_artist_to_dto(artist) for artist in track.artists],
        external_urls=_external_urls_dict(track.external_urls),
    )
