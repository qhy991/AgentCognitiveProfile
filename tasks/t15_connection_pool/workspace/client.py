"""HTTP API client with connection pooling and retry logic.

Usage:
    client = APIClient("https://api.example.com")
    client.get("/users")
    client.post("/users", json={"name": "Alice"})
"""

from pool import ConnectionPool
from request import Request
from exceptions import APIError, ConnectionError, PoolExhaustedError
from auth import AuthProvider


class APIClient:
    """A simple HTTP client with connection pooling."""

    def __init__(self, base_url, auth=None, pool_size=10, max_retries=3):
        self.base_url = base_url.rstrip("/")
        self.pool = ConnectionPool(pool_size)
        self.auth = auth
        self.max_retries = max_retries

    def get(self, path, headers=None):
        """Send a GET request."""
        return self._send("GET", path, headers=headers)

    def post(self, path, json=None, headers=None):
        """Send a POST request."""
        return self._send("POST", path, json=json, headers=headers)

    def put(self, path, json=None, headers=None):
        """Send a PUT request."""
        return self._send("PUT", path, json=json, headers=headers)

    def delete(self, path, headers=None):
        """Send a DELETE request."""
        return self._send("DELETE", path, headers=headers)

    def _send(self, method, path, json=None, headers=None):
        """Send a request with retry logic."""
        url = f"{self.base_url}{path}"
        all_headers = dict(headers or {})

        if self.auth:
            auth_header = self.auth.get_header()
            if auth_header:
                all_headers.update(auth_header)

        request = Request(method=method, url=url, json=json, headers=all_headers)

        last_error = None
        for attempt in range(self.max_retries + 1):
            conn = None
            try:
                conn = self.pool.acquire()
                response = conn.send(request)
                self.pool.release(conn)
                return response
            except ConnectionError as e:
                last_error = e
                if conn is not None:
                    # Connection might be bad — release it so it's
                    # removed from the pool
                    self.pool.release(conn, healthy=False)
                if attempt < self.max_retries:
                    continue
            except Exception as e:
                last_error = e
                if conn is not None:
                    self.pool.release(conn)
                raise

        raise APIError(
            f"Request failed after {self.max_retries + 1} attempts: {last_error}"
        )