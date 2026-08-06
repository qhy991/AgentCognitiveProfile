"""Record generation utilities for testing."""


def generate_records(count):
    """Generate synthetic records for testing."""
    types = ["alpha", "beta", "gamma", "delta"]
    departments = ["engineering", "sales", "marketing"]
    records = []
    for i in range(count):
        records.append({
            "id": i + 1,
            "first": f"user{i}",
            "last": f"test{i}",
            "type": types[i % 4],
            "department": departments[i % 3],
            "metadata": {
                "created": f"2024-{1 + i % 12:02d}-{1 + i % 28:02d}",
                "source": "api",
                "tags": [f"tag{j}" for j in range(i % 10)],
                "history": [{"ts": j, "action": f"update_{j}"} for j in range(i % 20)],
            },
            "metrics": {
                "a": i * 1.5,
                "b": i * 2.3,
                "c": i * 0.7,
                "nested_counts": {f"k{j}": j * i for j in range(min(i, 5))},
            },
        })
    return records