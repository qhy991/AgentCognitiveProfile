"""Data processing pipeline for transforming records.

Processes batches of records through a series of transformations:
filtering, enrichment, normalization, and aggregation.
"""

import copy


class DataPipeline:
    """A data processing pipeline that transforms records."""

    def __init__(self):
        self._stages = []

    def add_stage(self, name, transform_fn):
        self._stages.append((name, transform_fn))

    def process(self, records):
        """Run all records through the pipeline."""
        result = records
        for name, transform_fn in self._stages:
            result = transform_fn(result)
        return result


class RecordEnricher:
    """Enriches records with additional computed fields."""

    def __init__(self, reference_data):
        self._ref = reference_data

    def enrich(self, records):
        """Add computed fields to each record in-place."""
        for record in records:
            record["full_name"] = f"{record.get('first', '')} {record.get('last', '')}".strip()
            record["category"] = self._ref.get(record.get("type"), "unknown")
            metrics = record.get("metrics", {})
            record["score"] = (
                metrics.get("a", 0) * 0.5 +
                metrics.get("b", 0) * 0.3 +
                metrics.get("c", 0) * 0.2
            )
        return records


class Normalizer:
    """Normalizes record fields to standard formats."""

    def normalize(self, records):
        """Normalize field values in-place."""
        for record in records:
            for field in ("first", "last", "department"):
                if field in record:
                    record[field] = record[field].strip().title()
            if "metrics" in record:
                normalized_metrics = {}
                for k, v in record["metrics"].items():
                    if isinstance(v, (int, float)):
                        normalized_metrics[k] = round(float(v), 2)
                    else:
                        normalized_metrics[k] = v
                record["metrics"] = normalized_metrics
        return records