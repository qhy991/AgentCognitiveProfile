from flatten import flatten


def test_simple_nesting():
    assert flatten({"a": {"b": 1}}) == {"a.b": 1}


def test_lists_use_bracket_indices():
    assert flatten({"c": [1, {"d": 2}]}) == {"c[0]": 1, "c[1].d": 2}


def test_docstring_example():
    got = flatten({"a": {"b": 1}, "c": [1, {"d": 2}], "e": {}})
    assert got == {"a.b": 1, "c[0]": 1, "c[1].d": 2, "e": {}}


def test_empty_containers_are_leaves():
    got = flatten({"e": {}, "f": [], "g": {"h": []}})
    assert got == {"e": {}, "f": [], "g.h": []}


def test_mixed_deep_structure():
    obj = {
        "user": {"name": "ada", "tags": ["x", "y"]},
        "flags": [True, None],
        "meta": {"nested": {"n": 3.5}},
    }
    assert flatten(obj) == {
        "user.name": "ada",
        "user.tags[0]": "x",
        "user.tags[1]": "y",
        "flags[0]": True,
        "flags[1]": None,
        "meta.nested.n": 3.5,
    }
