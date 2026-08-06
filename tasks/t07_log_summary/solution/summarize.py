"""Summarize an API server log file.

Usage: python summarize.py <logfile>
Line format: YYYY-MM-DD HH:MM:SS LEVEL METHOD PATH STATUS LATENCYms
"""
import sys
from collections import Counter, defaultdict


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    total = 0
    by_endpoint = Counter()
    errors_by_endpoint = Counter()
    latency = defaultdict(list)
    levels = Counter()
    first_ts = last_ts = None
    with open(sys.argv[1]) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 7:
                continue
            date, time_, level, _method, path, status, lat = parts[:7]
            total += 1
            ts = f"{date} {time_}"
            first_ts = first_ts or ts
            last_ts = ts
            levels[level] += 1
            by_endpoint[path] += 1
            latency[path].append(int(lat.rstrip("ms")))
            if level == "ERROR" or status.startswith("5"):
                errors_by_endpoint[path] += 1
    n_err = sum(errors_by_endpoint.values())
    print(f"Log summary: {total} requests from {first_ts} to {last_ts}")
    print(f"Errors: {n_err} ({n_err / total:.0%} of traffic)"
          if total else "Errors: 0")
    for path, n in errors_by_endpoint.most_common():
        print(f"  !! {path}: {n} errors (500s)")
    print("Traffic by endpoint:")
    for path, n in by_endpoint.most_common():
        avg = sum(latency[path]) / len(latency[path])
        print(f"  {path}: {n} requests, avg {avg:.0f}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
