"""Deduplicate a merged contact export.

Usage: python clean_contacts.py <input.csv> <output.csv>

Two rows are considered the same person when they share a normalized
email address, or - when one of them has no email - when they share a
normalized name and the same phone digits. The first (most complete)
row wins; a kept row is backfilled with the email of a matching later
row if its own is empty.
"""
import csv
import re
import sys


def norm_email(email):
    return (email or "").strip().lower()


def norm_name(name):
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


def norm_phone(phone):
    digits = re.sub(r"\D", "", phone or "")
    return digits.lstrip("1") if len(digits) == 11 else digits


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip())
        return 2
    with open(sys.argv[1], newline="") as f:
        rows = list(csv.DictReader(f))

    kept = []
    by_email = {}
    by_name_phone = {}
    for row in rows:
        email = norm_email(row.get("email"))
        name_phone = (norm_name(row.get("name")), norm_phone(row.get("phone")))
        if email and email in by_email:
            continue
        if name_phone in by_name_phone:
            existing = by_name_phone[name_phone]
            if email and not norm_email(existing.get("email")):
                existing["email"] = row["email"].strip()
                by_email[email] = existing
            continue
        clean = {
            "name": re.sub(r"\s+", " ", (row.get("name") or "").strip()),
            "email": (row.get("email") or "").strip(),
            "phone": (row.get("phone") or "").strip(),
        }
        kept.append(clean)
        if email:
            by_email[email] = clean
        by_name_phone[name_phone] = clean

    with open(sys.argv[2], "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "phone"])
        writer.writeheader()
        writer.writerows(kept)
    return 0


if __name__ == "__main__":
    sys.exit(main())
