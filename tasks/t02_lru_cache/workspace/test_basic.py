from lru import LRUCache


def test_put_and_get():
    c = LRUCache(2)
    c.put("a", 1)
    assert c.get("a") == 1


def test_get_missing_returns_default():
    c = LRUCache(2)
    assert c.get("nope") is None
    assert c.get("nope", 42) == 42


def test_capacity_respected():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert len(c) == 2
