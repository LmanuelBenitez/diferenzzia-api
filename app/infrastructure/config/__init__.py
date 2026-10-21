"""Infrastructure config package.

Exposes the settings loader used across the application.
"""

from app.infrastructure.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
