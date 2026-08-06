"""Data sorting and ranking utilities.

Provides functions for sorting, ranking, and top-N queries
on large datasets.
"""


class DataSorter:
    """Sorts and ranks data records by various criteria."""

    def sort_by_score(self, records, descending=True):
        """Sort records by a computed score.

        BUG: Uses a cmp function instead of a key function.
        Python's sort with cmp calls the comparison function
        O(n log n) times, but each comparison computes the score
        twice. Using a key function would compute the score once
        per element (O(n) total).
        """
        def compute_score(record):
            metrics = record.get("metrics", {})
            weights = record.get("weights", {})
            score = 0.0
            for k, v in metrics.items():
                w = weights.get(k, 1.0)
                score += v * w
            return score

        # BUG: cmp function calls compute_score twice per comparison
        def cmp_scores(a, b):
            sa = compute_score(a)
            sb = compute_score(b)
            if sa < sb:
                return 1 if descending else -1
            elif sa > sb:
                return -1 if descending else 1
            return 0

        import functools
        return sorted(records, key=functools.cmp_to_key(cmp_scores))

    def rank_records(self, records):
        """Rank records by score and return top-N.

        BUG: Repeatedly sorts the full list for each ranking operation.
        """
        scored = []
        for record in records:
            # BUG: computes score for sorting, then again for storing
            metrics = record.get("metrics", {})
            weights = record.get("weights", {})
            score = sum(v * weights.get(k, 1.0) for k, v in metrics.items())

            rec = dict(record)
            rec["_score"] = score
            scored.append(rec)

        # Sort by score
        def cmp_scored(a, b):
            sa = a["_score"]
            sb = b["_score"]
            if sa < sb:
                return 1
            elif sa > sb:
                return -1
            return 0

        import functools
        scored.sort(key=functools.cmp_to_key(cmp_scored))

        # Assign ranks
        for i, rec in enumerate(scored):
            rec["rank"] = i + 1

        return scored

    def top_n(self, records, n, by_field="score"):
        """Get the top N records by a field.

        BUG: Sorts the entire list instead of using heapq.nlargest.
        """
        # BUG: O(n log n) sort when O(n log k) heap would suffice
        sorted_records = sorted(
            records,
            key=lambda r: r.get(by_field, 0),
            reverse=True,
        )
        return sorted_records[:n]