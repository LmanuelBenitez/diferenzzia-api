"""Infrastructure cache package.

Exposes concrete cache implementations.
"""

from app.infrastructure.cache.in_memory_cache import InMemoryCache

__all__ = ["InMemoryCache"]
