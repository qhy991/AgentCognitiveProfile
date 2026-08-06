import json

from config import load_config


def test_loads_wellformed_file(tmp_path):
    p = tmp_path / "conf.json"
    p.write_text(json.dumps({"host": "example.com", "port": 9000,
                             "debug": True, "timeout": 5}))
    cfg = load_config(str(p))
    assert cfg["host"] == "example.com"
    assert cfg["port"] == 9000
    assert cfg["debug"] is True
    assert cfg["timeout"] == 5
