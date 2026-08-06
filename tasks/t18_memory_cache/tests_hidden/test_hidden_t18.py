"""Hidden tests for t18_memory_cache — expired entry accumulation.

3 correctness tests + 2 memory/resource tests.
Buggy: correctness=1.0, memory=0.0 → 0.6
Solution: all pass → 1.0
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cache import TTLCache


# --- Correctness tests ---

def test_basic_get_put():
    """Basic get/put operations should work."""
    cache = TTLCache(max_size=10, default_ttl=60)
    cache.put("a", 1)
    assert cache.get("a") == 1
    assert cache.get("missing") is None
    assert cache.get("missing", "default") == "default"


def test_ttl_expiration():
    """Entries should expire after TTL."""
    cache = TTLCache(max_size=10, default_ttl=0.01)  # 10ms TTL
    cache.put("a", 1)
    assert cache.get("a") == 1  # still fresh
    time.sleep(0.02)  # wait for expiry
    assert cache.get("a") is None  # should be expired


def test_max_size_eviction():
    """Old entries should be evicted when cache is full."""
    cache = TTLCache(max_size=3, default_ttl=60)
    for i in range(5):
        cache.put(f"key{i}", i)
    # Cache should have at most 3 entries
    assert cache.size() <= 3


# --- Resource tests ---

def test_expired_entries_cleaned_up():
    """Expired entries should not accumulate in the cache."""
    cache = TTLCache(max_size=100, default_ttl=0.01)
    # Insert many entries with short TTL
    for i in range(100):
        cache.put(f"key{i}", i)
    time.sleep(0.03)  # Let them expire
    # Access a few entries — should trigger cleanup
    for i in range(10):
        cache.get(f"key{i}")
    # After accessing expired entries, they should be cleaned up
    # The cache should not have 100 stale entries
    assert cache.size() < 100, \
        f"Cache has {cache.size()} entries, many should be cleaned up"


def test_cache_does_not_accumulate_expired():
    """After many put/get cycles with short TTLs, cache should not grow."""
    cache = TTLCache(max_size=50, default_ttl=0.005)
    for cycle in range(20):
        for i in range(30):
            cache.put(f"k{cycle}_{i}", i)
        time.sleep(0.006)
        for i in range(30):
            cache.get(f"k{cycle}_{i}")
    # After many cycles, cache should not be bloated with expired entries
    assert cache.size() <= 50, \
        f"Cache has {cache.size()} entries, should be <= 50"