"""Data aggregation utilities for the pipeline."""


class Aggregator:
    """Aggregates records by specified fields."""

    def aggregate(self, records, by_field):
        """Group records by a field and compute summary stats."""
        groups = {}
        for record in records:
            key = record.get(by_field, "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(record)

        result = {}
        for key, group in groups.items():
            result[key] = {
                "count": len(group),
                "avg_score": sum(r.get("score", 0) for r in group) / len(group),
                "records": group,
            }
        return result