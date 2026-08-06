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


def load():
    if os.path.exists(PATH):
        with open(PATH) as f:
            return json.load(f)
    return []


def save(items):
    with open(PATH, "w") as f:
        json.dump(items, f)


def main():
    cmd = sys.argv[1]
    items = load()
    if cmd == "add":
        items.append({"text": " ".join(sys.argv[2:]), "done": False})
        save(items)
        print("added")
    elif cmd == "list":
        for i, it in enumerate(items):
            print(i + 1, it["text"])
    elif cmd == "done":
        n = int(sys.argv[2])
        items[n]["done"] = True
        save(items)
        print("done")


if __name__ == "__main__":
    main()
