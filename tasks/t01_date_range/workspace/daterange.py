from datetime import date, timedelta


def parse_date(s):
    """Parse a YYYY-MM-DD string into a date object."""
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def date_range(start, end):
    """Return every date from start to end inclusive, as YYYY-MM-DD strings.

    If start is after end, return an empty list.
    """
    a, b = parse_date(start), parse_date(end)
    out = []
    cur = a
    while cur < b:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return out
