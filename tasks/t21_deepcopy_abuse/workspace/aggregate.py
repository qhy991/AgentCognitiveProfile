"""Data aggregation utilities for the pipeline."""


class Aggregator:
    """Aggregates records by specified fields."""

    def aggregate(self, records, by_field):
        """Group records by a field and compute summary stats.

        BUG: unnecessarily creates deep copies of records.
        """
        import copy
        groups = {}
        for record in records:
            # BUG: deep copy for grouping
            rec = copy.deepcopy(record)
            key = rec.get(by_field, "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(rec)

        result = {}
        for key, group in groups.items():
            result[key] = {
                "count": len(group),
                "avg_score": sum(r.get("score", 0) for r in group) / len(group),
                "records": group,
            }
        return result