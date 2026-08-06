#!/usr/bin/env python3
"""Extract behavior (trajectory-style) metrics from a Claude Code
stream-json transcript. These are the manipulation-check variables: they
measure whether a personality variant actually changed HOW the agent
works, independent of whether it solved the task.

Parsing is best-effort and defensive: unknown or malformed lines are
skipped, so metric extraction never fails a run.
"""
import json
import re
from pathlib import Path

READ_TOOLS = {"Read", "Grep", "Glob", "LS"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_CMD = re.compile(r"\b(cat|ls|head|tail|grep|rg|find|wc)\b")
WRITE_CMD = re.compile(r"(>>?|\btee\b|\bsed\s+-i|\bmv\b|\bcp\b|\bpatch\b)")
TEST_CMD = re.compile(r"\b(pytest|unittest|python[0-9.]*\s+-m\s+pytest)\b")


def extract_metrics(transcript_path):
    m = {
        "n_assistant_msgs": 0,
        "narration_chars": 0,
        "n_tool_calls": 0,
        "tool_counts": {},
        "reads_before_first_edit": 0,
        "n_test_runs": 0,
        "n_files_touched": 0,
        "todo_writes": 0,
        "num_turns": None,
        "total_cost_usd": None,
        "duration_ms": None,
        "output_tokens": None,
        "is_error": None,
        "model": None,
    }
    files_touched = set()
    first_edit_seen = False
    path = Path(transcript_path)
    if not path.exists():
        return m
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            etype = ev.get("type")
            if etype == "system" and ev.get("subtype") == "init":
                m["model"] = ev.get("model")
            elif etype == "assistant":
                msg = ev.get("message") or {}
                content = msg.get("content") or []
                if not isinstance(content, list):
                    continue
                m["n_assistant_msgs"] += 1
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type")
                    if btype == "text":
                        m["narration_chars"] += len(block.get("text") or "")
                    elif btype == "tool_use":
                        name = block.get("name") or "?"
                        inp = block.get("input") or {}
                        m["n_tool_calls"] += 1
                        m["tool_counts"][name] = m["tool_counts"].get(name, 0) + 1
                        if name == "TodoWrite":
                            m["todo_writes"] += 1
                        if name in EDIT_TOOLS:
                            first_edit_seen = True
                            fp = inp.get("file_path")
                            if fp:
                                files_touched.add(fp)
                        elif name in READ_TOOLS and not first_edit_seen:
                            m["reads_before_first_edit"] += 1
                        elif name == "Bash":
                            cmd = inp.get("command") or ""
                            if TEST_CMD.search(cmd):
                                m["n_test_runs"] += 1
                            if not first_edit_seen:
                                if WRITE_CMD.search(cmd):
                                    first_edit_seen = True
                                elif READ_CMD.search(cmd):
                                    m["reads_before_first_edit"] += 1
            elif etype == "result":
                m["num_turns"] = ev.get("num_turns")
                m["total_cost_usd"] = ev.get("total_cost_usd")
                m["duration_ms"] = ev.get("duration_ms")
                m["is_error"] = ev.get("is_error")
                usage = ev.get("usage") or {}
                m["output_tokens"] = usage.get("output_tokens")
    m["n_files_touched"] = len(files_touched)
    return m


if __name__ == "__main__":
    import sys
    print(json.dumps(extract_metrics(sys.argv[1]), indent=2))
