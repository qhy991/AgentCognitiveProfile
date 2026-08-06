"""Environment variable parser — converts env vars to nested dicts.

Convention: double-underscore separates nested keys.
    APP__DATABASE__HOST=localhost  →  {"database": {"host": "localhost"}}
    APP__SERVER__PORT=8080         →  {"server": {"port": "8080"}}
"""

import os


def parse_env_prefix(prefix):
    """Parse all environment variables starting with `prefix` into a nested dict.

    Keys are split by '__' to create nested structure.
    Values are type-coerced: integers, floats, booleans, and 'null' → None.
    """
    result = {}
    prefix_upper = prefix.upper()

    for key, value in os.environ.items():
        if not key.startswith(prefix_upper):
            continue

        # Strip prefix and leading underscores
        suffix = key[len(prefix_upper):]
        while suffix.startswith("_"):
            suffix = suffix[1:]

        if not suffix:
            continue

        parts = suffix.lower().split("__")
        value = _coerce(value)

        # Navigate / create nested dict structure
        node = result
        for part in parts[:-1]:
            if part not in node:
                node[part] = {}
            node = node[part]
        node[parts[-1]] = value

    return result


def _coerce(value):
    """Try to convert string value to the appropriate Python type."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null" or value.lower() == "none":
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value