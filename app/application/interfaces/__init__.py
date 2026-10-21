"""Application interfaces (ports) package.

These Protocols define the boundaries the application layer depends on.
Concrete implementations live in the infrastructure layer and are injected
via FastAPI's dependency injection.
"""

from app.application.interfaces.cache_repository import CacheRepository

__all__ = ["CacheRepository"]
