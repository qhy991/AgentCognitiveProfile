"""Hidden tests for t15_connection_pool — connection pool resource leak.

The bug: when release(conn, healthy=False) is called (connection error),
the connection is marked unhealthy but NOT removed from _acquired and
no new connection is created. This causes the pool to shrink with each
error until it's exhausted.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool import ConnectionPool, Connection
from exceptions import ConnectionError, PoolExhaustedError


def test_acquire_and_release():
    """Normal acquire-release cycle should work."""
    pool = ConnectionPool(3)
    conn = pool.acquire()
    assert pool.available_count == 2
    assert pool.acquired_count == 1
    pool.release(conn)
    assert pool.available_count == 3
    assert pool.acquired_count == 0


def test_unhealthy_release_replaces_connection():
    """After releasing an unhealthy connection, pool should have a replacement."""
    pool = ConnectionPool(3)
    conn = pool.acquire()
    pool.release(conn, healthy=False)
    # After unhealthy release, the pool should still function
    assert pool.acquired_count == 0, \
        f"unhealthy conn should be removed from acquired, got {pool.acquired_count}"
    assert pool.available_count == 3, \
        f"pool should have 3 available connections after replacement, got {pool.available_count}"


def test_pool_survives_multiple_errors():
    """After many errors, pool should still have all connections."""
    pool = ConnectionPool(5)
    original_total = pool.available_count + pool.acquired_count

    for i in range(10):
        conn = pool.acquire()
        # Simulate error: release as unhealthy
        pool.release(conn, healthy=False)

    current_total = pool.available_count + pool.acquired_count
    assert current_total == original_total, \
        f"pool should maintain {original_total} total connections after errors, got {current_total}"
    assert pool.acquired_count == 0, \
        f"all connections should be released, got {pool.acquired_count}"


def test_pool_does_not_exhaust_after_errors():
    """After errors, pool should still be usable for subsequent requests."""
    pool = ConnectionPool(3)
    # Simulate 2 errors
    for _ in range(2):
        conn = pool.acquire()
        pool.release(conn, healthy=False)
    # Should still be able to acquire 3 connections
    conns = []
    for _ in range(3):
        conns.append(pool.acquire())
    assert len(conns) == 3, f"should acquire 3 connections, got {len(conns)}"
    for c in conns:
        pool.release(c)


def test_healthy_connections_are_reused():
    """Healthy connections should be returned to the pool for reuse."""
    pool = ConnectionPool(3)
    conn1 = pool.acquire()
    pool.release(conn1, healthy=True)
    conn2 = pool.acquire()
    # Should get the same connection back
    assert conn1 is conn2, "healthy connection should be reused"
    pool.release(conn2)