"""Thread-safe lock wrapper.

Provides a simple lock with timeout support.
"""

import threading


class SafeLock:
    """A wrapper around threading.Lock with timeout support."""

    def __init__(self):
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, *args):
        self._lock.release()

    def acquire(self, timeout=None):
        return self._lock.acquire(timeout=timeout)

    def release(self):
        self._lock.release()

    def locked(self):
        return self._lock.locked()