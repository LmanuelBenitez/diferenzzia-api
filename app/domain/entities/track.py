"""Track entity.

Pure domain entity representing a Spotify track. The field names and shape
intentionally mirror the Spotify Web API track object because the frontend
consumes that structure directly.
"""

from dataclasses import dataclass, field

from app.domain.entities.album import Album
from app.domain.entities.artist import Artist


@dataclass(frozen=True)
class Track:
    """A music track.

    Attributes:
        id: Spotify unique identifier.
        name: Track display name.
        duration_ms: Duration in milliseconds.
        popularity: Popularity score between 0 and 100.
        preview_url: 30-second preview URL, or ``None`` if unavailable.
        explicit: Whether the track has explicit content.
        track_number: Track position within its disc.
        disc_number: Disc number the track belongs to.
        album: Album the track belongs to.
        artists: Track-level artists.
        external_urls: Mapping of external service name to URL.
    """

    id: str
    name: str
    duration_ms: int
    popularity: int
    preview_url: str | None
    explicit: bool
    track_number: int
    disc_number: int
    album: Album
    artists: list[Artist] = field(default_factory=list)
    external_urls: dict[str, str] = field(default_factory=dict)
