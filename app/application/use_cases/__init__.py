"""Application use cases package.

Each use case represents a single business action and depends only on the
application interfaces (ports), never on concrete infrastructure.
"""

from app.application.use_cases.get_artist import GetArtistUseCase
from app.application.use_cases.get_top_tracks import GetTopTracksUseCase

__all__ = ["GetArtistUseCase", "GetTopTracksUseCase"]
