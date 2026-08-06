"""Hidden tests for t12_config_deep_merge — deep merge of nested configs.

The bug is in _deep_merge(): when both base[key] and override[key] are
dicts, the override replaces the entire subtree instead of merging recursively.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config, _deep_merge


def test_deep_merge_preserves_nested_keys():
    """Deep merge should keep nested keys from base that are not in override."""
    base = {"database": {"host": "localhost", "port": 5432}}
    override = {"database": {"host": "db.example.com"}}
    result = _deep_merge(base, override)
    assert result["database"]["host"] == "db.example.com"
    assert result["database"]["port"] == 5432, \
        f"port should be preserved from base, got {result['database']}"


def test_deep_merge_recursive_nested():
    """Deep merge should work on deeply nested structures."""
    base = {
        "app": {
            "database": {"host": "localhost", "pool": {"min": 1, "max": 5}},
            "cache": {"ttl": 300}
        }
    }
    override = {
        "app": {
            "database": {"pool": {"max": 20}},
        }
    }
    result = _deep_merge(base, override)
    assert result["app"]["database"]["host"] == "localhost"
    assert result["app"]["database"]["pool"]["min"] == 1
    assert result["app"]["database"]["pool"]["max"] == 20
    assert result["app"]["cache"]["ttl"] == 300


def test_config_load_dict_then_env():
    """Config should deep-merge dict defaults with overrides."""
    config = Config()
    config.load_dict({
        "database": {"host": "localhost", "port": 5432, "name": "myapp",
                      "pool": {"min_size": 2, "max_size": 10}}
    })
    config.load_dict({"database": {"host": "prod-db.example.com"}})

    merged = config.to_dict()
    assert merged["database"]["host"] == "prod-db.example.com"
    assert merged["database"]["port"] == 5432, \
        f"port should be preserved from base, got {merged['database']}"
    assert merged["database"]["pool"]["min_size"] == 2, \
        f"pool.min_size should be preserved from base"


def test_config_deep_merge_does_not_replace_whole_subtree():
    """Loading a partial override should not wipe sibling keys."""
    config = Config()
    config.load_dict({
        "server": {"host": "0.0.0.0", "port": 8080, "debug": False},
        "logging": {"level": "info", "format": "json"}
    })
    config.load_dict({
        "server": {"port": 9090}
    })
    merged = config.to_dict()
    assert merged["server"]["host"] == "0.0.0.0"
    assert merged["server"]["port"] == 9090
    assert merged["server"]["debug"] is False
    assert merged["logging"]["level"] == "info"


def test_config_multiple_layers_deep_merge():
    """Three layers should all deep-merge correctly."""
    config = Config()
    config.load_dict({"app": {"name": "myapp", "db": {"host": "localhost", "port": 5432}}})
    config.load_dict({"app": {"db": {"host": "staging"}}})
    config.load_dict({"app": {"db": {"port": 9999}}})
    merged = config.to_dict()
    assert merged["app"]["name"] == "myapp"
    assert merged["app"]["db"]["host"] == "staging"
    assert merged["app"]["db"]["port"] == 9999