"""Data sorting and ranking utilities.

Provides functions for sorting, ranking, and top-N queries
on large datasets.
"""

import heapq


class DataSorter:
    """Sorts and ranks data records by various criteria."""

    def _compute_score(self, record):
        """Compute a weighted score for a record."""
        metrics = record.get("metrics", {})
        weights = record.get("weights", {})
        return sum(v * weights.get(k, 1.0) for k, v in metrics.items())

    def sort_by_score(self, records, descending=True):
        """Sort records by computed score using key function (O(n) score computations)."""
        return sorted(records, key=self._compute_score, reverse=descending)

    def rank_records(self, records):
        """Rank records by score and return with ranks."""
        # Compute score once per record and store
        scored = []
        for record in records:
            rec = dict(record)
            rec["_score"] = self._compute_score(record)
            scored.append(rec)

        # Sort by score using key function
        scored.sort(key=lambda r: r["_score"], reverse=True)

        # Assign ranks
        for i, rec in enumerate(scored):
            rec["rank"] = i + 1

        return scored

    def top_n(self, records, n, by_field="score"):
        """Get the top N records using heapq for O(n log k) performance."""
        if n >= len(records):
            key = lambda r: r.get(by_field, 0)
            return sorted(records, key=key, reverse=True)
        return heapq.nlargest(n, records, key=lambda r: r.get(by_field, 0))