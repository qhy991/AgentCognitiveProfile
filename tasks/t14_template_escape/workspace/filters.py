"""Built-in template filters."""


def filter_upper(value):
    """Convert to uppercase."""
    return str(value).upper()


def filter_lower(value):
    """Convert to lowercase."""
    return str(value).lower()


def filter_title(value):
    """Title case."""
    return str(value).title()


def filter_length(value):
    """Return length of value."""
    if hasattr(value, "__len__"):
        return len(value)
    return 0


def filter_default(value, fallback=""):
    """Return fallback if value is falsy."""
    return value if value else fallback


DEFAULT_FILTERS = {
    "upper": filter_upper,
    "lower": filter_lower,
    "title": filter_title,
    "length": filter_length,
    "default": filter_default,
}