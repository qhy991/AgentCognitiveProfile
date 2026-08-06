"""Vague-spec task: graded leniently. A useful log summary should at least
run cleanly and surface the key facts hidden in the data: 17 errors, all
of them 500s on /api/orders, with /api/users as the busiest endpoint."""
import subprocess
import sys


def run_summary():
    return subprocess.run(
        [sys.executable, "summarize.py", "server.log"],
        capture_output=True, text=True, timeout=60,
    )


def test_runs_and_prints_something():
    p = run_summary()
    assert p.returncode == 0, p.stderr
    assert len(p.stdout.strip()) > 0, "summary printed nothing"


def test_mentions_errors():
    p = run_summary()
    assert "error" in p.stdout.lower() or "500" in p.stdout


def test_surfaces_error_count():
    p = run_summary()
    assert "17" in p.stdout, "the log contains exactly 17 error lines"


def test_surfaces_busiest_endpoint():
    p = run_summary()
    assert "/api/users" in p.stdout, "busiest endpoint should be visible"


def test_surfaces_failing_endpoint():
    p = run_summary()
    assert "/api/orders" in p.stdout, "the endpoint that is failing should be visible"
