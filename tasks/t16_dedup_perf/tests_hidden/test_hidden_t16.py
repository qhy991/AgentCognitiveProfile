"""Hidden tests for t16_dedup_perf — O(n²) deduplication.

3 correctness tests + 2 performance tests.
Buggy: correctness=1.0, performance=0.0 → 0.6
Solution: all pass → 1.0
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dedup import deduplicate, deduplicate_by_key


# --- Correctness tests ---

def test_deduplicate_basic():
    """Basic deduplication should work."""
    assert deduplicate([1, 2, 3]) == [1, 2, 3]
    assert deduplicate([1, 1, 2, 2, 3, 1]) == [1, 2, 3]
    assert deduplicate([]) == []
    assert deduplicate(["a", "b", "a", "c"]) == ["a", "b", "c"]


def test_deduplicate_by_key():
    """Deduplication by key should work."""
    items = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 1, "name": "Alice2"},
    ]
    result = deduplicate_by_key(items, key_func=lambda x: x["id"])
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"


def test_deduplicate_order_preserved():
    """Order should be preserved (first occurrence kept)."""
    items = [3, 1, 2, 1, 3, 4]
    assert deduplicate(items) == [3, 1, 2, 4]


# --- Performance tests ---

def test_performance_small():
    """Small lists should be fast."""
    items = list(range(1000)) * 2
    t0 = time.perf_counter()
    result = deduplicate(items)
    elapsed = time.perf_counter() - t0
    assert len(result) == 1000
    assert elapsed < 0.05, f"Too slow for 2000 items: {elapsed:.3f}s"


def test_performance_large():
    """Large lists should be processed in reasonable time."""
    # Create a list with 10000 unique items
    items = []
    for i in range(10000):
        items.append(f"item-{i}")
        items.append(f"item-{i}")  # duplicate

    t0 = time.perf_counter()
    result = deduplicate_by_key(items, key_func=lambda x: x)
    elapsed = time.perf_counter() - t0

    assert len(result) == 10000, f"Expected 10000 unique, got {len(result)}"
    assert elapsed < 0.2, \
        f"Large dedup took {elapsed:.2f}s (should be < 0.2s, O(n²) issue?)"