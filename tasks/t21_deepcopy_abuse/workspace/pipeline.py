"""Data processing pipeline for transforming records.

Processes batches of records through a series of transformations:
filtering, enrichment, normalization, and aggregation.
"""

import copy


class DataPipeline:
    """A data processing pipeline that transforms records.

    Each stage receives a list of records and returns a new list.
    BUG: The pipeline uses deepcopy() at every stage, creating
    unnecessary copies of large nested objects. This is extremely
    wasteful for large datasets.
    """

    def __init__(self):
        self._stages = []

    def add_stage(self, name, transform_fn):
        """Add a transformation stage to the pipeline."""
        self._stages.append((name, transform_fn))

    def process(self, records):
        """Run all records through the pipeline.

        BUG: deepcopy() on every stage for every record creates
        massive memory overhead. For N records and M stages,
        this creates N*M deep copies.
        """
        result = records
        for name, transform_fn in self._stages:
            # BUG: unnecessary deep copy of every record
            result = [copy.deepcopy(r) for r in result]
            result = transform_fn(result)
        return result


class RecordEnricher:
    """Enriches records with additional computed fields."""

    def __init__(self, reference_data):
        self._ref = reference_data

    def enrich(self, records):
        """Add computed fields to each record.

        BUG: deep copies each record before modification.
        """
        enriched = []
        for record in records:
            # BUG: deep copy of large nested record
            rec = copy.deepcopy(record)
            rec["full_name"] = f"{rec.get('first', '')} {rec.get('last', '')}".strip()
            rec["category"] = self._ref.get(rec.get("type"), "unknown")
            # Add computed metrics
            metrics = rec.get("metrics", {})
            rec["score"] = (
                metrics.get("a", 0) * 0.5 +
                metrics.get("b", 0) * 0.3 +
                metrics.get("c", 0) * 0.2
            )
            enriched.append(rec)
        return enriched


class Normalizer:
    """Normalizes record fields to standard formats."""

    def normalize(self, records):
        """Normalize field values in each record.

        BUG: deep copies each record before modification.
        """
        normalized = []
        for record in records:
            # BUG: another deep copy
            rec = copy.deepcopy(record)
            # Normalize string fields
            for field in ("first", "last", "department"):
                if field in rec:
                    rec[field] = rec[field].strip().title()
            # Normalize metrics
            if "metrics" in rec:
                normalized_metrics = {}
                for k, v in rec["metrics"].items():
                    if isinstance(v, (int, float)):
                        normalized_metrics[k] = round(float(v), 2)
                    else:
                        normalized_metrics[k] = v
                rec["metrics"] = normalized_metrics
            normalized.append(rec)
        return normalized