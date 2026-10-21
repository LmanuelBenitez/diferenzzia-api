"""Cache repository port.

Defines the abstract contract for a key/value cache with TTL support.
Concrete implementations (in-memory, Redis, etc.) live in the
infrastructure layer.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class CacheRepository(Protocol):
    """Abstract cache with time-to-live semantics."""

    def get(self, key: str) -> object | None:
        """Return the cached value for ``key`` if present and not expired.

        Args:
            key: Cache key.

        Returns:
            The cached value, or ``None`` if missing or expired.
        """
        ...

    def set(self, key: str, value: object) -> None:
        """Store ``value`` under ``key`` using the configured TTL.

        Args:
            key: Cache key.
            value: Value to store.
        """
        ...

    def delete(self, key: str) -> None:
        """Remove a single entry from the cache.

        Args:
            key: Cache key to remove.
        """
        ...

    def clear(self) -> None:
        """Remove all entries from the cache."""
        ...
