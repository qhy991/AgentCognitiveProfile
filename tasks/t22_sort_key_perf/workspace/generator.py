"""Data generation utilities for testing the sorter."""


def generate_weighted_records(count):
    """Generate records with metrics and weights for sorting."""
    import random
    random.seed(42)
    records = []
    for i in range(count):
        records.append({
            "id": i + 1,
            "name": f"item-{i+1}",
            "metrics": {
                "quality": random.uniform(0, 100),
                "relevance": random.uniform(0, 100),
                "freshness": random.uniform(0, 100),
                "popularity": random.uniform(0, 100),
            },
            "weights": {
                "quality": 0.4,
                "relevance": 0.3,
                "freshness": 0.2,
                "popularity": 0.1,
            },
        })
    return records