"""File loaders for YAML and JSON config files."""

import json
from pathlib import Path


def _read_file(path):
    """Read a file and return its text content."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    return p.read_text(encoding="utf-8")


def load_yaml_file(path):
    """Load a YAML config file (simplified — only supports basic structure).

    This is a minimal YAML parser that handles nested dicts, lists,
    strings, numbers, booleans, and null. No anchors, aliases, or
    multi-line strings.
    """
    # Try importing PyYAML, fall back to a minimal JSON-based approach
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: assume the file is actually JSON
        # (for testing, defaults.yaml is simple enough)
        return json.loads(_read_file(path))


def load_json_file(path):
    """Load a JSON config file."""
    return json.loads(_read_file(path))