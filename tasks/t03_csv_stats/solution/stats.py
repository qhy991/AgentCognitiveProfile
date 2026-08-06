import csv
import io


def column_mean(csv_text, column):
    """Return the mean of a numeric column in the given CSV text.

    Empty / whitespace-only and non-numeric cells are skipped. Returns
    None when the column holds no numeric values. Raises ValueError when
    the column is not present in the header.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    fieldnames = reader.fieldnames or []
    if column not in fieldnames:
        raise ValueError(f"column not found: {column}")
    total, n = 0.0, 0
    for row in reader:
        val = (row.get(column) or "").strip()
        if not val:
            continue
        try:
            num = float(val)
        except ValueError:
            continue
        total += num
        n += 1
    if n == 0:
        return None
    return total / n
