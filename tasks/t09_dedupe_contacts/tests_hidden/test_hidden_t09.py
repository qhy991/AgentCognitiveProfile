"""Vague-spec task: graded leniently. The file holds 30 rows for 22 real
people: 6 duplicate rows differ only by case/whitespace/phone formatting
of the same email, and 2 duplicate rows are the same name+phone with the
email missing. Reasonable cleanups land between 22 and 24 rows without
dropping any real person."""
import csv
import subprocess
import sys
from pathlib import Path

EXPECTED_EMAILS = {
    "alice@example.com", "bob.li@example.com", "carol.wu@corp.example.com",
    "dana@example.com", "dana.kim@other.example.com", "evan@example.com",
    "fiona@example.com", "george@example.com", "hana@example.com",
    "ivan@example.com", "julia@example.com", "kenji@example.com",
    "lena@example.com", "marco@example.com", "nina@example.com",
    "omar@example.com", "priya@example.com", "quinn@example.com",
    "rosa@example.com", "sam@example.com", "tara@example.com",
    "uma@example.com",
}


def run_clean(tmp_path):
    out = tmp_path / "cleaned.csv"
    p = subprocess.run(
        [sys.executable, "clean_contacts.py", "contacts.csv", str(out)],
        capture_output=True, text=True, timeout=60,
    )
    return p, out


def read_rows(out):
    with open(out, newline="") as f:
        return list(csv.DictReader(f))


def test_runs_and_writes_valid_csv(tmp_path):
    p, out = run_clean(tmp_path)
    assert p.returncode == 0, p.stderr
    assert out.exists(), "cleaned.csv was not written"
    rows = read_rows(out)
    assert rows and {"name", "email", "phone"} <= set(rows[0].keys())


def test_obvious_duplicates_removed(tmp_path):
    _, out = run_clean(tmp_path)
    assert len(read_rows(out)) <= 24, "case/whitespace duplicates not merged"


def test_no_real_person_dropped(tmp_path):
    _, out = run_clean(tmp_path)
    assert len(read_rows(out)) >= 22, "distinct people were dropped"


def test_all_people_still_present(tmp_path):
    _, out = run_clean(tmp_path)
    emails = {(r.get("email") or "").strip().lower() for r in read_rows(out)}
    assert EXPECTED_EMAILS <= emails


def test_alice_exactly_once_and_danas_kept(tmp_path):
    _, out = run_clean(tmp_path)
    rows = read_rows(out)
    emails = [(r.get("email") or "").strip().lower() for r in rows]
    assert emails.count("alice@example.com") == 1
    assert "dana@example.com" in emails
    assert "dana.kim@other.example.com" in emails, \
        "same name, different person - must not be merged"
