from ratelimit import SlidingWindowLimiter


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def make(limit=3, window=10):
    clock = FakeClock()
    return SlidingWindowLimiter(limit=limit, window=window, clock=clock), clock


def test_up_to_limit_allowed():
    lim, clock = make()
    assert [lim.allow() for _ in range(3)] == [True, True, True]


def test_limit_plus_one_denied():
    lim, clock = make()
    for _ in range(3):
        assert lim.allow() is True
    assert lim.allow() is False, "request number limit+1 must be denied"


def test_allowed_again_after_window():
    lim, clock = make()
    for _ in range(3):
        lim.allow()
    assert lim.allow() is False
    clock.t = 11.0
    assert lim.allow() is True


def test_exact_window_boundary_expires():
    lim, clock = make(limit=1, window=10)
    clock.t = 0.0
    assert lim.allow() is True
    clock.t = 10.0
    assert lim.allow() is True, "event exactly `window` old must not count"


def test_sliding_partial_expiry():
    lim, clock = make(limit=3, window=10)
    clock.t = 0.0
    lim.allow()
    clock.t = 1.0
    lim.allow()
    clock.t = 2.0
    lim.allow()
    clock.t = 10.5
    assert lim.allow() is True, "event at t=0 has expired, one slot free"
    assert lim.allow() is False, "window still holds `limit` events"
