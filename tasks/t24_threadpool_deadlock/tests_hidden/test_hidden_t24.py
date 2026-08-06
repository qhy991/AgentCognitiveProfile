"""Hidden tests for t24_threadpool_deadlock.

Tests that the thread pool can handle nested task submission
without deadlocking.
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pool import ThreadPool


def test_basic_execution():
    """Basic task execution should work."""
    pool = ThreadPool(2)
    pool.start()
    result = pool.execute_and_wait(lambda x: x * 2, 21)
    assert result == 42
    pool.shutdown()


def test_multiple_tasks():
    """Multiple independent tasks should work."""
    pool = ThreadPool(2)
    pool.start()
    results = []
    for i in range(5):
        results.append(pool.execute_and_wait(lambda x: x * x, i))
    assert results == [0, 1, 4, 9, 16]
    pool.shutdown()


def test_nested_subtasks():
    """Nested task submission should not deadlock."""
    pool = ThreadPool(2)
    pool.start()

    def outer():
        # Submit a subtask from within a pool task
        inner_result = pool.execute_and_wait(lambda x: x * 3, 7)
        return inner_result + 10

    result = pool.execute_and_wait(outer)
    assert result == 31  # 7*3 + 10
    pool.shutdown()


def test_deep_nesting():
    """Deeply nested subtasks should not deadlock."""
    pool = ThreadPool(2)
    pool.start()

    def level3():
        return 1

    def level2():
        return pool.execute_and_wait(level3) + 1

    def level1():
        return pool.execute_and_wait(level2) + 1

    result = pool.execute_and_wait(level1)
    assert result == 3  # 1 + 1 + 1
    pool.shutdown()


def test_concurrent_subtasks():
    """Multiple concurrent tasks each with subtasks should work."""
    pool = ThreadPool(4)
    pool.start()

    def task_with_subtask(base):
        sub = pool.execute_and_wait(lambda x: x * 2, base)
        return sub + 1

    # Submit multiple tasks concurrently
    tasks = [pool.submit(task_with_subtask, i) for i in range(10)]
    results = [t.wait(timeout=10) for t in tasks]

    assert results == [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    pool.shutdown()