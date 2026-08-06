class LRUCache:
    """A least-recently-used cache holding at most `capacity` items.

    When the cache is full, inserting a new key must evict the item that
    was least recently used, where "used" means either read via get()
    or written via put().
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self._data = {}

    def get(self, key, default=None):
        if key in self._data:
            self._data[key] = self._data.pop(key)
            return self._data[key]
        return default

    def put(self, key, value):
        if key in self._data:
            del self._data[key]
        elif len(self._data) >= self.capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)
