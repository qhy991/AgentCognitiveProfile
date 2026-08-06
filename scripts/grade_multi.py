#!/usr/bin/env python3
"""Multi-dimension task grading for cognitive profile differentiation.

Unlike grade.py (binary pass/fail), this grades on multiple dimensions:
  1. correctness (0-1): Hidden test pass rate
  2. performance (0-1): Normalized execution speed
  3. minimality (0-1): How few changes were made
  4. quality (0-1): Code structure and readability

Different cognitive profiles naturally excel at different dimensions,
creating differentiation even when all profiles pass basic tests.

Output: {"correctness": 0.8, "performance": 0.6, "minimality": 0.9,
         "quality": 0.4, "overall": 0.68}
"""

import json
import math
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def _run_pytest(cwd, test_paths, timeout=120):
    """Run pytest and return (passed, total) from junit XML."""
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        xml_path = f.name
    cmd = [
        sys.executable, "-m", "pytest", "-q", "--tb=no",
        "-p", "no:cacheprovider", f"--junitxml={xml_path}",
    ] + [str(p) for p in test_paths]
    try:
        subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 0, 0
    try:
        root = ET.parse(xml_path).getroot()
    except Exception:
        return 0, 0
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return 0, 0
    total = int(suite.get("tests", 0) or 0)
    bad = sum(int(suite.get(k, 0) or 0)
              for k in ("failures", "errors", "skipped"))
    return max(total - bad, 0), total


def score_correctness(workspace_dir, task_dir):
    """Score correctness: hidden test pass rate (0-1)."""
    task_dir = Path(task_dir)
    workspace_dir = Path(workspace_dir)
    hidden_tests = list((task_dir / "tests_hidden").glob("*.py"))
    if not hidden_tests:
        return 1.0

    # Copy workspace and tests to temp dir (same as grade.py)
    import shutil
    tmp = Path(tempfile.mkdtemp(prefix="grade_multi_"))
    try:
        dst = tmp / "ws"
        shutil.copytree(workspace_dir, dst)
        for junk in ("CLAUDE.md", "AGENTS.md"):
            p = dst / junk
            if p.exists():
                p.unlink()
        for p in hidden_tests:
            shutil.copy(p, dst / p.name)
        test_files = [dst / p.name for p in hidden_tests]
        passed, total = _run_pytest(dst, test_files)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if total == 0:
        return 0.0
    return passed / total


def score_performance(workspace_dir, task_dir):
    """Score performance: normalized execution speed.

    Reads the perf_benchmark.py file in workspace (if exists) and
    measures execution time. Normalizes to 0-1 where 1.0 is fast.
    """
    task_dir = Path(task_dir)
    bench_file = Path(workspace_dir) / "perf_benchmark.py"
    if not bench_file.exists():
        return 1.0  # no benchmark → assume fast

    # Run the benchmark and parse its output
    try:
        result = subprocess.run(
            [sys.executable, str(bench_file)],
            cwd=str(workspace_dir),
            capture_output=True, text=True, timeout=30,
        )
        # Benchmark should output: "time: <seconds>"
        for line in result.stdout.splitlines():
            if line.startswith("time:"):
                elapsed = float(line.split(":")[1].strip())
                # Normalize: 0.01s → 1.0, 1.0s → 0.5, 10s → 0.0
                score = max(0.0, min(1.0, 1.0 / (1.0 + math.log10(max(elapsed, 0.001) * 100))))
                return score
    except Exception:
        pass
    return 0.5  # default if benchmark fails


def score_minimality(workspace_dir, task_dir):
    """Score minimality: how few lines were changed.

    Compares the workspace against the original workspace to count
    lines changed. Fewer changes → higher score.
    """
    task_dir = Path(task_dir)
    original = task_dir / "workspace"
    current = Path(workspace_dir)

    total_changed = 0
    total_lines = 0

    for orig_file in original.rglob("*.py"):
        rel = orig_file.relative_to(original)
        curr_file = current / rel
        orig_lines = orig_file.read_text().splitlines()
        curr_lines = curr_file.read_text().splitlines() if curr_file.exists() else []
        total_lines += len(orig_lines)

        # Simple diff: count lines changed
        orig_set = set(orig_lines)
        curr_set = set(curr_lines)
        changed = len(orig_set.symmetric_difference(curr_set))
        total_changed += changed

    if total_lines == 0:
        return 1.0

    change_ratio = total_changed / total_lines
    # 0% change → 1.0, 10% change → 0.8, 50% → 0.3, 100% → 0.0
    score = max(0.0, 1.0 - change_ratio * 1.5)
    return min(1.0, score)


def score_quality(workspace_dir):
    """Score code quality: presence of good patterns.

    Checks for: docstrings, type hints, descriptive variable names,
    proper error handling.
    """
    workspace = Path(workspace_dir)
    py_files = list(workspace.rglob("*.py"))
    if not py_files:
        return 0.5

    scores = []
    for f in py_files:
        if f.name.startswith("test_"):
            continue
        content = f.read_text()
        fs = 0.0

        # Has docstrings
        if '"""' in content or "'''" in content:
            fs += 0.25
        # Has type hints (simplistic check)
        if ": " in content and "def " in content:
            fs += 0.25
        # Has error handling
        if "try:" in content or "raise " in content:
            fs += 0.25
        # Uses descriptive names (lines > 20 chars on average)
        lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        if lines and sum(len(l) for l in lines) / len(lines) > 25:
            fs += 0.25

        scores.append(fs)

    return sum(scores) / len(scores) if scores else 0.5


def grade_multi(workspace_dir, task_dir):
    """Grade a workspace on multiple dimensions.

    Returns:
        {"correctness": 0.9, "performance": 0.7, "minimality": 0.8,
         "quality": 0.6, "overall": 0.75}
    """
    c = score_correctness(workspace_dir, task_dir)
    p = score_performance(workspace_dir, task_dir)
    m = score_minimality(workspace_dir, task_dir)
    q = score_quality(workspace_dir)

    # Weighted overall score
    overall = c * 0.4 + p * 0.25 + m * 0.2 + q * 0.15

    return {
        "correctness": round(c, 4),
        "performance": round(p, 4),
        "minimality": round(m, 4),
        "quality": round(q, 4),
        "overall": round(overall, 4),
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python grade_multi.py <workspace_dir> <task_dir>")
        sys.exit(2)
    result = grade_multi(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))