"""Worker thread for testing concurrent counter operations."""

import threading


def worker_increment(counter, count, delta=1):
    """Worker function that increments a counter many times."""
    for _ in range(count):
        counter.increment(delta)


def worker_get_and_increment(counter, count, results_list, idx):
    """Worker that calls get_and_increment and records results."""
    for _ in range(count):
        val = counter.get_and_increment()
        results_list.append(val)


def worker_mixed(counter, increments, gets):
    """Worker that does a mix of increments and gets."""
    for _ in range(increments):
        counter.increment()
    for _ in range(gets):
        counter.get()