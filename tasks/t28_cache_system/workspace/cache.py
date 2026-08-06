"""Caching system with TTL and LRU eviction."""

import time
import hashlib
import json


class ComputeCache:
    """Caches expensive computation results.

    BUG 1: Cache key computed with json.dumps + hashlib on every lookup.
    BUG 2: No size limit — memory grows unbounded.
    """

    def __init__(self):
        self._cache = {}

    def _make_key(self, *args, **kwargs):
        """Create a cache key from arguments.

        BUG 1: json.dumps + hashlib is expensive for large args.
        """
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, *args, **kwargs):
        """Get a cached value."""
        key = self._make_key(*args, **kwargs)
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self._cache[key]
            return None
        return value

    def set(self, value, ttl=300, *args, **kwargs):
        """Store a value in the cache.

        BUG 2: No size limit check.
        """
        key = self._make_key(*args, **kwargs)
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)

    def compute(self, func, *args, ttl=300, **kwargs):
        """Compute a value or return cached result."""
        cached = self.get(*args, **kwargs)
        if cached is not None:
            return cached
        result = func(*args, **kwargs)
        self.set(result, ttl, *args, **kwargs)
        return result

    def size(self):
        return len(self._cache)

    def clear(self):
        self._cache.clear()


def expensive_computation(n):
    """Simulate an expensive computation."""
    time.sleep(0.001)
    return n * n