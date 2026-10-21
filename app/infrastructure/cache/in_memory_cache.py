"""In-memory cache implementation with TTL.

A simple thread-safe dictionary-based cache. Suitable for the MVP: data
changes very rarely so an in-process cache is enough. The interface allows
swapping in Redis later without touching the application layer.
"""

import threading
import time
from dataclasses import dataclass

from app.application.interfaces.cache_repository import CacheRepository


@dataclass
class _CacheEntry:
    """A cached value together with its expiration timestamp.

    Attributes:
        value: The cached payload.
        expires_at: Monotonic timestamp after which the entry is stale.
    """

    value: object
    expires_at: float

    def is_expired(self) -> bool:
        """Return whether the entry has passed its expiration time.

        Returns:
            ``True`` if expired, ``False`` otherwise.
        """
        return time.monotonic() >= self.expires_at


class InMemoryCache(CacheRepository):
    """Thread-safe in-memory cache with a configurable TTL."""

    def __init__(self, ttl_seconds: int) -> None:
        """Initialize the cache.

        Args:
            ttl_seconds: Time-to-live applied to every entry, in seconds.

        Raises:
            ValueError: If ``ttl_seconds`` is not positive.
        """
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl_seconds = ttl_seconds
        self._store: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> object | None:
        """Return the cached value for ``key`` if present and not expired.

        Args:
            key: Cache key.

        Returns:
            The cached value, or ``None`` if missing or expired.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: object) -> None:
        """Store ``value`` under ``key`` using the configured TTL.

        Args:
            key: Cache key.
            value: Value to store.
        """
        with self._lock:
            self._store[key] = _CacheEntry(
                value=value,
                expires_at=time.monotonic() + self._ttl_seconds,
            )

    def delete(self, key: str) -> None:
        """Remove a single entry from the cache.

        Args:
            key: Cache key to remove. No-op if missing.
        """
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()

    @property
    def ttl_seconds(self) -> int:
        """Return the configured TTL in seconds.

        Returns:
            The cache TTL in seconds.
        """
        return self._ttl_seconds
