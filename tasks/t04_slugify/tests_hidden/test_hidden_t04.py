from slug import slugify


def test_basic_punctuation():
    assert slugify("Hello, World!") == "hello-world"


def test_accents_folded_to_ascii():
    assert slugify("Crème Brûlée") == "creme-brulee"


def test_collapse_and_trim_hyphens():
    assert slugify("  --Weird__spacing--  ") == "weird-spacing"


def test_empty_input_untitled():
    assert slugify("") == "untitled"


def test_symbols_only_untitled():
    assert slugify("!!! ??? ***") == "untitled"


def test_digits_kept():
    assert slugify("Top 10 Things") == "top-10-things"


def test_truncation_to_60():
    assert slugify("a" * 70) == "a" * 60
    assert slugify("a" * 59 + " bbbb") == "a" * 59
