from lru import LRUCache


def test_basic_roundtrip():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1 and c.get("b") == 2


def test_eviction_without_reads():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert "a" not in c
    assert "b" in c and "c" in c


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert "b" not in c, "b was least recently used and should be evicted"
    assert "a" in c and "c" in c


def test_get_refreshes_recency_capacity3():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    c.get("a")
    c.get("b")
    c.put("d", 4)
    assert "c" not in c, "c was least recently used and should be evicted"
    assert "a" in c and "b" in c and "d" in c


def test_len_and_default():
    c = LRUCache(2)
    assert len(c) == 0
    assert c.get("missing", "dflt") == "dflt"
    c.put("x", 1)
    c.put("y", 2)
    c.put("z", 3)
    assert len(c) == 2
