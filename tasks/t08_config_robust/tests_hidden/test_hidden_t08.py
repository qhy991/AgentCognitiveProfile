"""Vague-spec task: graded leniently. Robust config loading should survive
missing files, malformed JSON, partial configs, and wrong types without
leaking raw low-level exceptions."""
import json

from config import load_config

EXPECTED_KEYS = {"host", "port", "debug", "timeout"}


def test_missing_file_returns_defaults(tmp_path):
    cfg = load_config(str(tmp_path / "does_not_exist.json"))
    assert isinstance(cfg, dict)
    assert EXPECTED_KEYS <= set(cfg)
    assert cfg["host"] == "localhost" and cfg["port"] == 8080


def test_malformed_json_handled(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{oops, this is not json")
    try:
        cfg = load_config(str(p))
    except json.JSONDecodeError:
        raise AssertionError("raw json.JSONDecodeError leaked to the caller")
    except FileNotFoundError:
        raise AssertionError("wrong exception type for malformed file")
    except Exception as e:
        assert len(str(e)) >= 10, "error should carry a helpful message"
    else:
        assert isinstance(cfg, dict) and EXPECTED_KEYS <= set(cfg)


def test_partial_config_filled_with_defaults(tmp_path):
    p = tmp_path / "partial.json"
    p.write_text(json.dumps({"port": 9000}))
    cfg = load_config(str(p))
    assert cfg["port"] == 9000
    assert cfg["host"] == "localhost"
    assert cfg["timeout"] == 30


def test_wrong_types_handled(tmp_path):
    p = tmp_path / "types.json"
    p.write_text(json.dumps({"port": "9000", "debug": "true"}))
    try:
        cfg = load_config(str(p))
    except Exception as e:
        assert len(str(e)) >= 10, "error should carry a helpful message"
    else:
        assert isinstance(cfg["port"], int), "port should end up an int"
        assert isinstance(cfg["debug"], bool), "debug should end up a bool"


def test_unknown_keys_tolerated(tmp_path):
    p = tmp_path / "extra.json"
    p.write_text(json.dumps({"host": "h.example.com", "shiny_new_key": 1}))
    cfg = load_config(str(p))
    assert cfg["host"] == "h.example.com"
    assert cfg["port"] == 8080
