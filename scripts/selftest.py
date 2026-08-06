#!/usr/bin/env python3
"""Validate the experiment scaffold itself (no Claude calls, no cost).

Checks, for every task:
  - the pristine buggy workspace scores < 1.0 on the hidden tests
    (otherwise the task cannot detect anything), and
  - the reference solution scores exactly 1.0
    (otherwise the hidden tests are wrong).

Also checks that the five personality variants exist and are reasonably
length-matched (so prompt length is not a confound).

Run this once after unpacking, and again after any edit to tasks/tests.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade import grade_run  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def check_variants():
    problems = []
    files = {p.stem[:4]: p for p in (ROOT / "variants").glob("p*.md")}
    expected = {p.stem[:4] for p in (ROOT / "profiles").glob("p*.yaml")}
    missing = expected - set(files)
    if missing:
        problems.append(f"missing variants: {sorted(missing)}")
    sizes = {p.stem: len(p.read_text()) for p in (ROOT / "variants").glob("p*.md")}
    if sizes:
        avg = sum(sizes.values()) / len(sizes)
        for name, size in sorted(sizes.items()):
            drift = (size - avg) / avg
            flag = "  <-- length drift >30%" if abs(drift) > 0.30 else ""
            print(f"  variant {name:<35} {size:>5} chars ({drift:+.0%}){flag}")
            if abs(drift) > 0.30:
                problems.append(f"variant {name} length drifts {drift:+.0%}")
    return problems


def check_task(task_dir):
    buggy = grade_run(task_dir / "workspace", task_dir)
    tmp = Path(tempfile.mkdtemp(prefix="selftest_"))
    try:
        solved_ws = tmp / "ws"
        shutil.copytree(task_dir / "workspace", solved_ws)
        for p in (task_dir / "solution").iterdir():
            if p.is_file():
                shutil.copy(p, solved_ws / p.name)
        solved = grade_run(solved_ws, task_dir)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bf, sf = buggy["hidden"]["frac"], solved["hidden"]["frac"]
    problems = []
    if sf < 1.0:
        problems.append(f"{task_dir.name}: reference solution scores {sf} (< 1.0)")
    if bf >= 1.0:
        problems.append(f"{task_dir.name}: buggy baseline already scores 1.0")
    vis = solved.get("visible")
    if vis and vis["frac"] < 1.0:
        problems.append(f"{task_dir.name}: solution breaks visible tests ({vis['frac']})")
    print(f"  {task_dir.name:<22} buggy={bf:.2f}  solution={sf:.2f}"
          f"{'  visible=' + format(vis['frac'], '.2f') if vis else ''}")
    return problems


def main():
    problems = []
    print("variants:")
    problems += check_variants()
    print("tasks (hidden-test pass fraction):")
    for task_dir in sorted((ROOT / "tasks").iterdir()):
        if (task_dir / "meta.json").exists():
            meta = json.loads((task_dir / "meta.json").read_text())
            n_files = len(list((task_dir / "tests_hidden").glob("*.py")))
            if n_files == 0:
                problems.append(f"{task_dir.name}: no hidden tests")
                continue
            problems += check_task(task_dir)
            _ = meta  # meta validated implicitly by grade_run
    if problems:
        print("\nSELFTEST FAILED:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("\nselftest OK: all tasks can detect failure and reward the fix.")


if __name__ == "__main__":
    main()
