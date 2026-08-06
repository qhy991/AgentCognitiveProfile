"""Connection pool — manages a fixed-size pool of reusable HTTP connections.

Each connection is a simulated HTTP connection that can be acquired,
used to send a request, and released back to the pool.
"""

import time
from exceptions import PoolExhaustedError, ConnectionError


class Connection:
    """A simulated HTTP connection."""

    _counter = 0

    def __init__(self):
        Connection._counter += 1
        self.id = Connection._counter
        self._healthy = True
        self._acquired_at = None

    def send(self, request):
        """Simulate sending an HTTP request.

        Raises ConnectionError if the connection is unhealthy.
        """
        if not self._healthy:
            raise ConnectionError(f"Connection {self.id} is unhealthy")
        # Simulate network latency
        time.sleep(0.001)
        return {
            "status": 200,
            "body": f"response from conn {self.id}",
            "request": {"method": request.method, "url": request.url},
        }

    def mark_unhealthy(self):
        """Mark this connection as unhealthy (e.g., after a network error)."""
        self._healthy = False

    @property
    def healthy(self):
        return self._healthy

    def __repr__(self):
        return f"Connection(id={self.id}, healthy={self._healthy})"


class ConnectionPool:
    """A fixed-size pool of reusable connections.

    Connections are acquired, used, and released back to the pool.
    Unhealthy connections are discarded and replaced.
    """

    def __init__(self, size):
        self._size = size
        self._available = []  # Stack of idle connections
        self._acquired = set()  # Connections currently in use
        # Pre-create connections
        for _ in range(size):
            self._available.append(Connection())

    @property
    def available_count(self):
        return len(self._available)

    @property
    def acquired_count(self):
        return len(self._acquired)

    def acquire(self):
        """Acquire a connection from the pool.

        Returns a Connection, or raises PoolExhaustedError if none available.
        """
        if not self._available:
            raise PoolExhaustedError(
                f"Connection pool exhausted ({self._size} connections in use)"
            )
        conn = self._available.pop()
        self._acquired.add(conn)
        conn._acquired_at = time.time()
        return conn

    def release(self, conn, healthy=True):
        """Release a connection back to the pool.

        If healthy=False, the connection is discarded and a new one is
        created to replace it.

        BUG: When healthy=False, the connection is marked unhealthy but
        is NOT removed from _acquired. This means it stays in _acquired
        forever, and the pool size effectively shrinks with each error.
        """
        if conn in self._acquired:
            if healthy:
                self._acquired.remove(conn)
                self._available.append(conn)
            else:
                conn.mark_unhealthy()
                # BUG: conn is never removed from _acquired
                # and no new connection is created to replace it
                # The fix should be:
                # self._acquired.remove(conn)
                # self._available.append(Connection())
        # If conn is not in _acquired, it's already been released (double release)

    def stats(self):
        """Return pool statistics."""
        return {
            "total": self._size,
            "available": self.available_count,
            "in_use": self.acquired_count,
            "healthy_available": sum(1 for c in self._available if c.healthy),
            "unhealthy": sum(1 for c in self._available if not c.healthy),
        }