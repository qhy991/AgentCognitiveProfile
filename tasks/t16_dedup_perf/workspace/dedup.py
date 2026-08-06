"""Data deduplication utilities.

Provides functions for removing duplicates from lists while
preserving order. Used in data processing pipelines.
"""


def deduplicate(items):
    """Remove duplicates from a list while preserving order.

    This is the stable deduplication function used throughout
    the codebase. It preserves the first occurrence of each item.

    Args:
        items: A list of hashable items.

    Returns:
        A new list with duplicates removed, in original order.
    """
    seen = []
    result = []
    for item in items:
        if item not in seen:
            seen.append(item)
            result.append(item)
    return result


def deduplicate_by_key(items, key_func):
    """Remove duplicates based on a key function.

    Keeps the first item for each unique key.
    BUG: Uses O(n²) algorithm — for each item, scans all previous
    keys to check for duplicates.

    Args:
        items: A list of items.
        key_func: A function that extracts the comparison key.

    Returns:
        A new list with duplicates removed, in original order.
    """
    seen_keys = []
    result = []
    for item in items:
        key = key_func(item)
        # BUG: O(n) scan per item → O(n²) total
        if key not in seen_keys:
            seen_keys.append(key)
            result.append(item)
    return result


def batch_deduplicate(batches, key_func):
    """Deduplicate across multiple batches of data.

    Processes each batch individually and then merges.
    """
    all_results = []
    for batch in batches:
        deduped = deduplicate_by_key(batch, key_func)
        all_results.extend(deduped)
    # Final dedup across batches
    return deduplicate_by_key(all_results, key_func)