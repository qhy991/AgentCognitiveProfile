"""Time-aware cache with TTL-based expiration.

Supports get, put, and automatic eviction of expired entries.
Uses a simple dict internally with periodic cleanup.
"""

import time
from eviction import EvictionPolicy
from stats import CacheStats


class TTLCache:
    """A cache that evicts entries after their TTL expires."""

    def __init__(self, max_size=1000, default_ttl=300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._data = {}  # {key: (value, expiry_time)}
        self._policy = EvictionPolicy()
        self._stats = CacheStats()

    def get(self, key, default=None):
        """Get a value from the cache. Returns default if missing or expired."""
        if key not in self._data:
            self._stats.miss()
            return default

        value, expiry = self._data[key]
        if time.time() > expiry:
            del self._data[key]
            self._stats.miss()
            return default

        self._stats.hit()
        self._policy.record_access(key)
        return value

    def put(self, key, value, ttl=None):
        """Store a value in the cache with optional TTL override."""
        if ttl is None:
            ttl = self.default_ttl
        expiry = time.time() + ttl

        # Clean up expired entries before inserting
        self._evict_expired()

        if key in self._data:
            self._data[key] = (value, expiry)
            self._policy.record_access(key)
            return

        if len(self._data) >= self.max_size:
            evict_key = self._policy.choose_victim(self._data.keys())
            if evict_key is not None:
                del self._data[evict_key]

        self._data[key] = (value, expiry)
        self._policy.record_access(key)

    def _evict_expired(self):
        """Remove all expired entries."""
        now = time.time()
        expired = [k for k, (v, exp) in self._data.items() if now > exp]
        for k in expired:
            del self._data[k]

    def delete(self, key):
        """Remove a key from the cache."""
        self._data.pop(key, None)

    def clear(self):
        """Remove all entries."""
        self._data.clear()
        self._stats.reset()

    def size(self):
        """Return the number of entries (including expired)."""
        return len(self._data)

    def stats(self):
        """Return cache statistics."""
        return self._stats.snapshot()

    def cleanup_expired(self):
        """Remove all expired entries from the cache."""
        return self._evict_expired()