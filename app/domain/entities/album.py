"""Album entity.

Pure domain entity representing a Spotify album (or single/compilation).
"""

from dataclasses import dataclass, field

from app.domain.entities.artist import Artist
from app.domain.entities.image import Image


@dataclass(frozen=True)
class Album:
    """A music album.

    Attributes:
        id: Spotify unique identifier.
        name: Album display name.
        album_type: One of ``album``, ``single`` or ``compilation``.
        total_tracks: Total number of tracks in the album.
        images: List of cover images, ordered from largest to smallest.
        release_date: Release date string (precision depends on Spotify).
        artists: Album-level artists.
        external_urls: Mapping of external service name to URL.
    """

    id: str
    name: str
    album_type: str
    total_tracks: int
    images: list[Image] = field(default_factory=list)
    release_date: str = ""
    artists: list[Artist] = field(default_factory=list)
    external_urls: dict[str, str] = field(default_factory=dict)
