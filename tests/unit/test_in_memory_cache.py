"""Unit tests for the ``InMemoryCache`` implementation."""

import time

import pytest

from app.infrastructure.cache.in_memory_cache import InMemoryCache


class TestInMemoryCache:
    """Tests for basic cache behavior."""

    def test_set_and_get_returns_value(self) -> None:
        """A stored value is returned by ``get``."""
        cache = InMemoryCache(ttl_seconds=60)
        cache.set("k", {"a": 1})
        assert cache.get("k") == {"a": 1}

    def test_get_missing_key_returns_none(self) -> None:
        """A missing key returns ``None``."""
        cache = InMemoryCache(ttl_seconds=60)
        assert cache.get("missing") is None

    def test_delete_removes_key(self) -> None:
        """``delete`` removes the entry."""
        cache = InMemoryCache(ttl_seconds=60)
        cache.set("k", 1)
        cache.delete("k")
        assert cache.get("k") is None

    def test_clear_empties_cache(self) -> None:
        """``clear`` removes all entries."""
        cache = InMemoryCache(ttl_seconds=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_entry_expires_after_ttl(self) -> None:
        """An entry past its TTL is treated as missing."""
        cache = InMemoryCache(ttl_seconds=1)
        cache.set("k", "v")
        time.sleep(1.1)
        assert cache.get("k") is None

    def test_non_positive_ttl_raises(self) -> None:
        """Constructing with a non-positive TTL must fail."""
        with pytest.raises(ValueError):
            InMemoryCache(ttl_seconds=0)

    def test_ttl_property_returns_configured_value(self) -> None:
        """The ``ttl_seconds`` property exposes the configured TTL."""
        cache = InMemoryCache(ttl_seconds=42)
        assert cache.ttl_seconds == 42
