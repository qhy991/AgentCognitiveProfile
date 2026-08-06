"""Cache exceptions."""


class CacheError(Exception):
    """Base cache error."""
    pass


class CacheFullError(CacheError):
    """Raised when the cache is full and eviction fails."""
    pass