import pytest

from stats import column_mean


def test_normal_mean():
    csv_text = "name,score\na,10\nb,20\nc,30\n"
    assert column_mean(csv_text, "score") == 20.0


def test_empty_cells_skipped():
    csv_text = "name,score\na,10\nb,\nc,20\nd,   \n"
    assert column_mean(csv_text, "score") == 15.0


def test_invalid_cells_skipped():
    csv_text = "name,score\na,10\nb,N/A\nc,abc\nd,20\n"
    assert column_mean(csv_text, "score") == 15.0


def test_all_empty_returns_none():
    csv_text = "name,score\na,\nb,N/A\n"
    assert column_mean(csv_text, "score") is None


def test_no_rows_returns_none():
    csv_text = "name,score\n"
    assert column_mean(csv_text, "score") is None


def test_missing_column_raises_valueerror():
    csv_text = "name,score\na,10\n"
    with pytest.raises(ValueError) as exc:
        column_mean(csv_text, "points")
    assert "points" in str(exc.value)
