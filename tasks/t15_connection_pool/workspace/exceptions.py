"""Exception classes for the API client."""


class APIError(Exception):
    """Base exception for API errors."""
    pass


class ConnectionError(APIError):
    """Raised when a connection-level error occurs."""
    pass


class PoolExhaustedError(APIError):
    """Raised when the connection pool is exhausted."""
    pass