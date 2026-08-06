"""Hidden tests for t20_nplusone_query — N+1 query optimization.

3 correctness + 2 performance tests.
Buggy: correctness=1.0, performance=0.0 → 0.6
Solution: all pass → 1.0
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import Database, UserStore
from fixtures import setup_database


def _setup():
    db = Database()
    setup_database(db)
    return db, UserStore(db)


# --- Correctness tests ---

def test_get_single_user():
    """Single user lookup should work."""
    _, store = _setup()
    user = store.get_user(1)
    assert user is not None
    assert user["name"] == "User-1"


def test_get_users_by_ids():
    """Batch user lookup should return correct results."""
    _, store = _setup()
    users = store.get_users_by_ids([1, 2, 3, 999])
    assert len(users) == 3
    assert {u["id"] for u in users} == {1, 2, 3}


def test_get_users_by_department():
    """Department lookup should enrich with manager names."""
    _, store = _setup()
    users = store.get_users_by_department("engineering")
    assert len(users) > 0
    # Users with manager_id should have manager_name
    for u in users:
        if u.get("manager_id"):
            assert "manager_name" in u, f"User {u['id']} missing manager_name"


# --- Performance tests ---

def test_performance_batch_lookup():
    """Batch lookup of 100 users should be fast (single query, not 100)."""
    _, store = _setup()
    ids = list(range(1, 101))
    t0 = time.perf_counter()
    users = store.get_users_by_ids(ids)
    elapsed = time.perf_counter() - t0
    assert len(users) == 100
    assert elapsed < 0.05, \
        f"100-user lookup took {elapsed:.3f}s (should be < 0.05s, N+1 issue?)"


def test_performance_department_report():
    """Department report should not make N queries for managers."""
    _, store = _setup()
    t0 = time.perf_counter()
    users = store.get_users_by_department("engineering")
    elapsed = time.perf_counter() - t0
    # Engineering has ~125 users, each with manager lookup
    # N+1 would take ~125 * 0.001s = 0.125s+
    assert elapsed < 0.05, \
        f"Department lookup took {elapsed:.3f}s (should be < 0.05s, N+1 issue?)"