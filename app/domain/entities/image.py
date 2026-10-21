"""Image entity.

Pure domain entity representing an image (album cover, artist picture, etc.).
No external dependencies — only the Python standard library.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Image:
    """A single image with its dimensions.

    Attributes:
        url: Public URL of the image.
        height: Image height in pixels, if known.
        width: Image width in pixels, if known.
    """

    url: str
    height: int | None = None
    width: int | None = None
