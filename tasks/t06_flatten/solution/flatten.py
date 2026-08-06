def flatten(obj):
    """Flatten a nested structure of dicts and lists into a flat dict."""
    out = {}

    def walk(value, path):
        if isinstance(value, dict) and value:
            for k, v in value.items():
                walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(value, list) and value:
            for i, v in enumerate(value):
                walk(v, f"{path}[{i}]")
        else:
            out[path] = value

    walk(obj, "")
    return out
