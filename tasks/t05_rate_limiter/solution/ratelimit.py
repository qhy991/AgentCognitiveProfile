class SlidingWindowLimiter:
    """Allow at most `limit` events per `window` seconds (sliding window).

    `clock` is a callable returning the current time in seconds. An event
    that happened exactly `window` seconds ago is outside the window and
    no longer counts.
    """

    def __init__(self, limit, window, clock):
        self.limit = limit
        self.window = window
        self.clock = clock
        self._events = []

    def allow(self):
        """Return True and record the event if it is allowed, else False."""
        now = self.clock()
        self._events = [t for t in self._events if t > now - self.window]
        if len(self._events) >= self.limit:
            return False
        self._events.append(now)
        return True
