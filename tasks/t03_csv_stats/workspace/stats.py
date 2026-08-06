import csv
import io


def column_mean(csv_text, column):
    """Return the mean of a numeric column in the given CSV text.

    See the project requirements for how empty / invalid cells and
    missing columns must be handled.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    total, n = 0.0, 0
    for row in reader:
        val = row[column]
        total += float(val)
        n += 1
    return total / n
