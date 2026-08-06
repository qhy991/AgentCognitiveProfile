from ratelimit import SlidingWindowLimiter


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_first_requests_allowed():
    clock = FakeClock()
    lim = SlidingWindowLimiter(limit=3, window=10, clock=clock)
    assert lim.allow() is True
    assert lim.allow() is True
    assert lim.allow() is True
