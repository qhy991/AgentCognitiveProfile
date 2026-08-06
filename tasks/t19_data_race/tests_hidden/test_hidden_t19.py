"""Hidden tests for t19_data_race — concurrent counter race condition.

All 5 tests check correctness under concurrent access.
Buggy: most tests fail due to race condition in get_and_increment.
Solution: all pass.
"""
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from counter import Counter
from worker import worker_increment, worker_get_and_increment


def test_single_thread_increment():
    """Single-threaded increment should work correctly."""
    c = Counter(0)
    for _ in range(100):
        c.increment()
    assert c.get() == 100


def test_single_thread_get_and_increment():
    """Single-threaded get_and_increment should work correctly."""
    c = Counter(0)
    values = []
    for _ in range(100):
        values.append(c.get_and_increment())
    # Values should be 0, 1, 2, ..., 99
    assert values == list(range(100)), f"Expected 0..99, got {values[:10]}..."


def test_concurrent_increment():
    """Concurrent increments should be atomic."""
    c = Counter(0)
    threads = []
    for _ in range(8):
        t = threading.Thread(target=worker_increment, args=(c, 5000))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.get() == 40000, \
        f"Expected 40000, got {c.get()} (race condition?)"


def test_concurrent_get_and_increment():
    """Concurrent get_and_increment should produce unique values."""
    c = Counter(0)
    results = []
    threads = []
    for i in range(8):
        t = threading.Thread(
            target=worker_get_and_increment, args=(c, 500, results, i))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 4000, f"Expected 4000 results, got {len(results)}"
    unique = set(results)
    assert len(unique) == len(results), \
        f"Found {len(results) - len(unique)} duplicate values (race condition!)"


def test_final_value_after_concurrent_get_and_increment():
    """After concurrent get_and_increment, final value should be total calls."""
    c = Counter(0)
    results = []
    threads = []
    for _ in range(8):
        t = threading.Thread(
            target=worker_get_and_increment, args=(c, 500, results, None))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.get() == 4000, \
        f"Expected final value 4000, got {c.get()} (race condition?)"