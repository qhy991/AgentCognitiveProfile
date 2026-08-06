"""Cache statistics tracking."""


class CacheStats:
    """Tracks hit/miss counts and ratios."""

    def __init__(self):
        self.hits = 0
        self.misses = 0

    def hit(self):
        self.hits += 1

    def miss(self):
        self.misses += 1

    def reset(self):
        self.hits = 0
        self.misses = 0

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def snapshot(self):
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "total": self.hits + self.misses,
        }