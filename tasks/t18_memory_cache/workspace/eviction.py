"""Eviction policy for the cache.

Implements a simple Least-Recently-Used (LRU) eviction strategy.
"""


class EvictionPolicy:
    """Tracks access order for LRU eviction."""

    def __init__(self):
        self._access_order = []  # most recent at the end

    def record_access(self, key):
        """Record that a key was accessed."""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def choose_victim(self, keys):
        """Choose a key to evict. Returns the least recently used key."""
        for key in self._access_order:
            if key in keys:
                return key
        # Fallback: return first key
        for key in keys:
            return key
        return None