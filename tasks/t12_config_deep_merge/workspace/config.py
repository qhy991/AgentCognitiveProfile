"""Configuration system — loads settings from YAML, JSON, and environment
variables, then deep-merges them in priority order.

Typical usage:
    config = Config()
    config.load_yaml("defaults.yaml")       # lowest priority
    config.load_env("APP_")                 # highest priority
    db_host = config.get("database.host")
"""

import os
import json
from pathlib import Path

from loader import load_yaml_file, load_json_file
from env import parse_env_prefix
from schema import validate_config


class Config:
    """Manages configuration from multiple sources, merged by priority."""

    def __init__(self):
        self._sources = []  # list of dicts, lowest priority first

    def load_yaml(self, path):
        """Load a YAML config file (lowest priority layer)."""
        data = load_yaml_file(path)
        self._sources.append(data)

    def load_json(self, path):
        """Load a JSON config file."""
        data = load_json_file(path)
        self._sources.append(data)

    def load_dict(self, data):
        """Load a plain dict as a config layer."""
        self._sources.append(data)

    def load_env(self, prefix):
        """Load environment variables with the given prefix (highest priority)."""
        data = parse_env_prefix(prefix)
        self._sources.append(data)

    def get(self, dotpath, default=None):
        """Get a config value by dot-separated path, e.g. 'database.host'."""
        merged = self.merge()
        keys = dotpath.split(".")
        node = merged
        for key in keys:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return default
        return node

    def merge(self):
        """Merge all loaded sources into a single dict.

        Later sources override earlier ones. Nested dicts should be
        deep-merged, not replaced wholesale.
        """
        result = {}
        for source in self._sources:
            result = _deep_merge(result, source)
        return result

    def to_dict(self):
        """Return the fully merged configuration as a dict."""
        return self.merge()


def _deep_merge(base, override):
    """Merge two dicts recursively. Values in `override` take precedence.

    BUG: When both base[key] and override[key] are dicts, this function
    should recursively merge them. Instead it replaces the entire subtree.
    """
    merged = dict(base)
    for key, value in override.items():
        merged[key] = value  # BUG: should deep-merge when both are dicts
    return merged