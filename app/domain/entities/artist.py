"""Artist entity.

Pure domain entity representing a Spotify artist. It mirrors the shape of
the Spotify Web API artist object but stays free of any external dependency.
"""

from dataclasses import dataclass, field

from app.domain.entities.image import Image


@dataclass(frozen=True)
class Artist:
    """A music artist.

    Attributes:
        id: Spotify unique identifier.
        name: Artist display name.
        uri: Spotify URI (e.g. ``spotify:artist:...``).
        external_urls: Mapping of external service name to URL. Usually
            ``{"spotify": "https://open.spotify.com/artist/..."}``.
        images: List of associated images, ordered from largest to smallest.
        genres: List of genre tags associated with the artist.
        popularity: Popularity score between 0 and 100.
        followers: Total number of followers.
    """

    id: str
    name: str
    uri: str
    external_urls: dict[str, str] = field(default_factory=dict)
    images: list[Image] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    popularity: int = 0
    followers: int = 0
