#!/usr/bin/env python3
"""A tiny team todo CLI.

Usage:
    python todo.py add <text...>
    python todo.py list
    python todo.py done <number>
"""
import json
import os
import sys

PATH = os.environ.get("TODO_FILE", "todo.json")
USAGE = __doc__.strip()


def load():
    if os.path.exists(PATH):
        try:
            with open(PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save(items):
    with open(PATH, "w") as f:
        json.dump(items, f, indent=2)


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main():
    if len(sys.argv) < 2:
        return fail("missing command")
    cmd = sys.argv[1]
    items = load()

    if cmd == "add":
        text = " ".join(sys.argv[2:]).strip()
        if not text:
            return fail("nothing to add")
        items.append({"text": text, "done": False})
        save(items)
        print(f"added #{len(items)}: {text}")
        return 0

    if cmd == "list":
        if not items:
            print("nothing to do!")
            return 0
        for i, it in enumerate(items, start=1):
            mark = "x" if it.get("done") else " "
            print(f"[{mark}] {i}. {it['text']}")
        return 0

    if cmd == "done":
        if len(sys.argv) < 3 or not sys.argv[2].isdigit():
            return fail("usage: done <number> (as shown by list)")
        n = int(sys.argv[2])
        if not 1 <= n <= len(items):
            return fail(f"no item number {n} (you have {len(items)})")
        items[n - 1]["done"] = True
        save(items)
        print(f"done: {items[n - 1]['text']}")
        return 0

    return fail(f"unknown command: {cmd}")


if __name__ == "__main__":
    sys.exit(main())
