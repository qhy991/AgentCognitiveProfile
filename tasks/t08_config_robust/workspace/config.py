import json

DEFAULTS = {
    "host": "localhost",
    "port": 8080,
    "debug": False,
    "timeout": 30,
}


def load_config(path):
    """Load the app configuration from a JSON file."""
    with open(path) as f:
        cfg = json.load(f)
    return cfg
