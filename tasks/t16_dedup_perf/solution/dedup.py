"""Data deduplication utilities.

Provides functions for removing duplicates from lists while
preserving order. Used in data processing pipelines.
"""


def deduplicate(items):
    """Remove duplicates from a list while preserving order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def deduplicate_by_key(items, key_func):
    """Remove duplicates based on a key function.

    Keeps the first item for each unique key.
    Uses O(n) algorithm with a set for seen keys.
    """
    seen_keys = set()
    result = []
    for item in items:
        key = key_func(item)
        if key not in seen_keys:
            seen_keys.add(key)
            result.append(item)
    return result


def batch_deduplicate(batches, key_func):
    """Deduplicate across multiple batches of data."""
    all_results = []
    for batch in batches:
        deduped = deduplicate_by_key(batch, key_func)
        all_results.extend(deduped)
    return deduplicate_by_key(all_results, key_func)