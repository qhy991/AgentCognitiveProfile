"""Hidden tests for t28_cache_system — 2 performance issues."""
import time, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cache import ComputeCache


def fast_compute(n):
    return n * n


def test_correctness_cache_hit():
    c = ComputeCache()
    r1 = c.compute(fast_compute, 5, ttl=60)
    r2 = c.compute(fast_compute, 5, ttl=60)
    assert r1 == 25 and r2 == 25


def test_correctness_cache_miss():
    c = ComputeCache()
    r = c.compute(fast_compute, 7, ttl=0.001)
    time.sleep(0.002)
    r2 = c.get(7)
    assert r == 49 and r2 is None


def test_correctness_different_args():
    c = ComputeCache()
    r1 = c.compute(fast_compute, 3)
    r2 = c.compute(fast_compute, 4)
    assert r1 == 9 and r2 == 16 and c.size() == 2


def test_performance_key_generation():
    """Key generation should be fast."""
    c = ComputeCache()
    t0 = time.perf_counter()
    for i in range(2000):
        c.compute(fast_compute, i, ttl=60)
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.3, f"Key gen: {elapsed:.3f}s (json.dumps?)"


def test_performance_memory_limit():
    """Cache should not grow unbounded."""
    c = ComputeCache()
    t0 = time.perf_counter()
    for i in range(20000):
        c.compute(fast_compute, i, ttl=60)
    elapsed = time.perf_counter() - t0
    assert c.size() <= 11000, f"Cache size {c.size()} (no limit?)"
    assert elapsed < 0.5, f"Memory: {elapsed:.3f}s"