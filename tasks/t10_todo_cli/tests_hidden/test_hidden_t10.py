"""Vague-spec task: graded leniently. A pleasant CLI should at least keep
the basic flows working, reflect done-status in the list, and never dump a
raw traceback at the user for predictable mistakes."""
import subprocess
import sys


def run(tmp_path, *args):
    return subprocess.run(
        [sys.executable, "todo.py", *args],
        capture_output=True, text=True, timeout=60,
        env={"TODO_FILE": str(tmp_path / "todo.json"), "PATH": "/usr/bin:/bin"},
    )


def output(p):
    return (p.stdout or "") + (p.stderr or "")


def test_add_then_list_shows_item(tmp_path):
    p = run(tmp_path, "add", "buy", "milk")
    assert p.returncode == 0, output(p)
    p = run(tmp_path, "list")
    assert p.returncode == 0
    assert "buy milk" in p.stdout


def test_done_marks_first_item(tmp_path):
    run(tmp_path, "add", "buy", "milk")
    run(tmp_path, "add", "walk", "dog")
    before = run(tmp_path, "list").stdout
    p = run(tmp_path, "done", "1")
    assert "Traceback" not in output(p)
    after = run(tmp_path, "list").stdout
    milk_lines = [l for l in after.splitlines() if "buy milk" in l]
    assert after != before, "list output should reflect the done status"
    if milk_lines:
        dog_lines = [l for l in after.splitlines() if "walk dog" in l]
        assert milk_lines[0] != dog_lines[0].replace("walk dog", "buy milk"), \
            "the DONE item (1: buy milk) should look different from the open one"


def test_done_out_of_range_is_friendly(tmp_path):
    run(tmp_path, "add", "only", "item")
    p = run(tmp_path, "done", "99")
    assert "Traceback" not in output(p), "raw traceback shown to the user"
    assert p.returncode != 0 or any(
        w in output(p).lower() for w in ("invalid", "no ", "not ", "error", "unknown")
    ), "out-of-range index should be reported to the user"


def test_list_with_no_file_is_clean(tmp_path):
    p = run(tmp_path, "list")
    assert p.returncode == 0
    assert "Traceback" not in output(p)


def test_no_arguments_shows_usage_not_traceback(tmp_path):
    p = run(tmp_path)
    assert "Traceback" not in output(p), "raw traceback shown to the user"
    assert output(p).strip() != "", "should print usage or an error hint"
