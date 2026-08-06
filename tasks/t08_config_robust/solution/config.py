import json
import os

DEFAULTS = {
    "host": "localhost",
    "port": 8080,
    "debug": False,
    "timeout": 30,
}


class ConfigError(Exception):
    """Raised when the configuration file cannot be used."""


def _coerce(key, value, default):
    kind = type(default)
    if isinstance(value, kind) and not (kind is int and isinstance(value, bool)):
        return value
    try:
        if kind is bool:
            if isinstance(value, str):
                return value.strip().lower() in ("1", "true", "yes", "on")
            return bool(value)
        if kind is int:
            return int(value)
        if kind is str:
            return str(value)
    except (TypeError, ValueError):
        pass
    return default


def load_config(path):
    """Load the app configuration from a JSON file, robustly.

    Missing file -> defaults. Malformed JSON -> ConfigError with a
    helpful message. Partial config -> missing keys filled from
    DEFAULTS. Wrong types -> coerced when sensible, else the default.
    Unknown keys are kept as-is.
    """
    if not os.path.exists(path):
        return dict(DEFAULTS)
    try:
        with open(path) as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"config file {path!r} is not valid JSON: {e}") from e
    if not isinstance(raw, dict):
        raise ConfigError(
            f"config file {path!r} must contain a JSON object")
    cfg = dict(DEFAULTS)
    for key, value in raw.items():
        if key in DEFAULTS:
            cfg[key] = _coerce(key, value, DEFAULTS[key])
        else:
            cfg[key] = value
    return cfg
