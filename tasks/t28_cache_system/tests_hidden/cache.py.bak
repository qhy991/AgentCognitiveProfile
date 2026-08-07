"""Caching system with TTL and LRU eviction."""

import time
from collections import OrderedDict


class ComputeCache:
    """Caches expensive computation results with LRU eviction."""

    def __init__(self, max_size=10000):
        self.max_size = max_size
        self._cache = OrderedDict()

    def _make_key(self, *args, **kwargs):
        """Create a cache key from arguments (simple tuple hash)."""
        return hash((args, tuple(sorted(kwargs.items()))))

    def get(self, *args, **kwargs):
        """Get a cached value, promoting the key on hit."""
        key = self._make_key(*args, **kwargs)
        entry = self._cache.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return value

    def set(self, value, ttl=300, *args, **kwargs):
        """Store a value in the cache, evicting oldest if needed."""
        key = self._make_key(*args, **kwargs)
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
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