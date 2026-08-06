#!/usr/bin/env python3
"""Grade an agent-modified workspace against a task's hidden tests.

Usage as a library:
    from grade import grade_run
    scores = grade_run(workspace_dir, task_dir)

Usage from the command line:
    python scripts/grade.py <workspace_dir> <task_dir>

The workspace is copied to a temp dir, hidden tests are copied in next to
it, and pytest runs there with --junitxml so results parse without extra
plugins. Visible tests (regression canaries) are re-run from the task's
ORIGINAL copies, so an agent editing the visible test files cannot game
that metric.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


def _run_pytest(cwd, test_paths, timeout):
    """Run pytest on the given files; return {'passed': int, 'total': int}
    parsed from junit XML, or None if pytest could not produce results."""
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        xml_path = f.name
    cmd = [
        sys.executable, "-m", "pytest", "-q", "--tb=no",
        "-p", "no:cacheprovider", f"--junitxml={xml_path}",
    ] + [str(p) for p in test_paths]
    try:
        subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    try:
        root = ET.parse(xml_path).getroot()
    except Exception:
        return None
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return None
    total = int(suite.get("tests", 0) or 0)
    bad = sum(int(suite.get(k, 0) or 0)
              for k in ("failures", "errors", "skipped"))
    return {"passed": max(total - bad, 0), "total": total}


def grade_run(workspace_dir, task_dir):
    """Return {'hidden': {...}, 'visible': {...} | None} for a workspace."""
    workspace_dir, task_dir = Path(workspace_dir), Path(task_dir)
    meta = json.loads((task_dir / "meta.json").read_text())
    n_declared = meta["n_hidden_tests"]
    timeout = meta.get("timeout_grade", 120)

    tmp = Path(tempfile.mkdtemp(prefix="grade_"))
    try:
        dst = tmp / "ws"
        shutil.copytree(workspace_dir, dst)
        for junk in ("CLAUDE.md", "AGENTS.md"):
            p = dst / junk
            if p.exists():
                p.unlink()

        # --- hidden tests ---
        hidden_files = []
        for p in sorted((task_dir / "tests_hidden").glob("*.py")):
            shutil.copy(p, dst / p.name)
            hidden_files.append(dst / p.name)
        res = _run_pytest(dst, hidden_files, timeout)
        passed = res["passed"] if res else 0
        # Denominator is the declared test count so collection crashes
        # (broken workspace) score 0 instead of erroring out.
        hidden = {
            "passed": min(passed, n_declared),
            "total": n_declared,
            "frac": round(min(passed, n_declared) / n_declared, 4),
        }

        # --- visible regression tests, from pristine task copies ---
        visible = None
        vis_names = meta.get("visible_tests", [])
        if vis_names:
            vis_files = []
            for name in vis_names:
                src = task_dir / "workspace" / name
                dst_name = f"test_original_{Path(name).name}"
                shutil.copy(src, dst / dst_name)
                vis_files.append(dst / dst_name)
            vres = _run_pytest(dst, vis_files, timeout)
            if vres and vres["total"] > 0:
                visible = {
                    "passed": vres["passed"],
                    "total": vres["total"],
                    "frac": round(vres["passed"] / vres["total"], 4),
                }
            else:
                visible = {"passed": 0, "total": len(vis_names), "frac": 0.0}
        return {"hidden": hidden, "visible": visible}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    print(json.dumps(grade_run(sys.argv[1], sys.argv[2]), indent=2))
