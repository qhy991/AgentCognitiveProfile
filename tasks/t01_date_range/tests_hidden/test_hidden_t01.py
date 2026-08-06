from daterange import date_range


def test_inclusive_endpoints():
    r = date_range("2024-01-01", "2024-01-03")
    assert r == ["2024-01-01", "2024-01-02", "2024-01-03"]


def test_length_of_week():
    r = date_range("2023-05-01", "2023-05-07")
    assert len(r) == 7


def test_same_day():
    assert date_range("2024-06-15", "2024-06-15") == ["2024-06-15"]


def test_leap_year_february():
    r = date_range("2024-02-28", "2024-03-01")
    assert r == ["2024-02-28", "2024-02-29", "2024-03-01"]


def test_start_after_end_empty():
    assert date_range("2024-01-05", "2024-01-01") == []


def test_output_format():
    r = date_range("2024-11-30", "2024-12-02")
    assert all(isinstance(s, str) and len(s) == 10 for s in r)
    assert r[0] == "2024-11-30" and r[-1] == "2024-12-02"
