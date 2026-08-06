"""Thread-safe counter with atomic increment.

Provides a Counter class that can be safely used from multiple threads.
Uses a simple lock for thread safety.
"""

import threading
from lock import SafeLock
from exceptions import CounterError


class Counter:
    """A thread-safe counter with atomic operations."""

    def __init__(self, initial=0):
        self._value = initial
        self._lock = SafeLock()

    def increment(self, delta=1):
        """Atomically increment the counter by delta."""
        with self._lock:
            self._value += delta

    def get(self):
        """Get the current counter value."""
        with self._lock:
            return self._value

    def get_and_increment(self, delta=1):
        """Atomically get the current value and then increment.

        Returns the value BEFORE incrementing.
        """
        with self._lock:
            old = self._value
            self._value += delta
        return old

    def reset(self):
        """Reset the counter to zero."""
        with self._lock:
            self._value = 0