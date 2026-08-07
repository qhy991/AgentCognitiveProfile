"""Hidden tests for t22_sort_key_perf — sort key optimization.

3 correctness + 2 performance tests.
Buggy: correctness=1.0, performance=0.0 → 0.6
Solution: all pass → 1.0
"""
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sorter import DataSorter
from generator import generate_weighted_records


# --- Correctness tests ---

def test_sort_by_score():
    """Sorting should produce correct order."""
    sorter = DataSorter()
    records = generate_weighted_records(100)
    result = sorter.sort_by_score(records)
    assert len(result) == 100
    # Verify descending order
    for i in range(len(result) - 1):
        s1 = sorter._compute_score(result[i])
        s2 = sorter._compute_score(result[i + 1])
        assert s1 >= s2, f"Sort order violation at index {i}"


def test_rank_records():
    """Ranking should assign correct ranks."""
    sorter = DataSorter()
    records = generate_weighted_records(50)
    result = sorter.rank_records(records)
    assert len(result) == 50
    assert result[0]["rank"] == 1
    assert result[-1]["rank"] == 50
    # Verify descending order
    assert result[0]["_score"] >= result[-1]["_score"]


def test_top_n():
    """Top-N should return correct number of records."""
    sorter = DataSorter()
    records = generate_weighted_records(100)
    result = sorter.top_n(records, 10, by_field="_score")
    # Will use the score field if available, otherwise sort by the field
    assert len(result) <= 10


# --- Performance tests ---

def test_performance_sort_large():
    """Sorting 5000 records should be fast with key function."""
    sorter = DataSorter()
    records = generate_weighted_records(5000)

    t0 = time.perf_counter()
    result = sorter.sort_by_score(records)
    elapsed = time.perf_counter() - t0

    assert len(result) == 5000
    assert elapsed < 0.2, \
        f"Sorting 5000 records took {elapsed:.3f}s (should be < 0.2s, cmp issue?)"


def test_performance_rank_large():
    """Ranking 5000 records should be fast."""
    sorter = DataSorter()
    records = generate_weighted_records(5000)

    t0 = time.perf_counter()
    result = sorter.rank_records(records)
    elapsed = time.perf_counter() - t0

    assert len(result) == 5000
    assert elapsed < 0.3, \
        f"Ranking 5000 records took {elapsed:.3f}s (should be < 0.3s)"