"""Hidden tests for t21_deepcopy_abuse — unnecessary deep copy.

3 correctness + 2 performance tests.
Buggy: correctness=1.0, performance=0.0 → 0.6
Solution: all pass → 1.0
"""
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipeline import DataPipeline, RecordEnricher, Normalizer
from aggregate import Aggregator
from generator import generate_records


# --- Correctness tests ---

def test_pipeline_correctness():
    """Pipeline should produce correct results."""
    pipeline = DataPipeline()
    enricher = RecordEnricher({"alpha": "type-a", "beta": "type-b"})
    normalizer = Normalizer()
    pipeline.add_stage("enrich", enricher.enrich)
    pipeline.add_stage("normalize", normalizer.normalize)

    records = generate_records(10)
    result = pipeline.process(records)

    assert len(result) == 10
    assert "full_name" in result[0]
    assert "category" in result[0]
    assert "score" in result[0]


def test_aggregate_correctness():
    """Aggregation should produce correct results."""
    enricher = RecordEnricher({"alpha": "type-a"})
    normalizer = Normalizer()
    agg = Aggregator()

    records = generate_records(20)
    records = enricher.enrich(records)
    records = normalizer.normalize(records)
    result = agg.aggregate(records, "department")

    total = sum(v["count"] for v in result.values())
    assert total == 20, f"Expected 20 records, got {total}"


def test_enricher_adds_fields():
    """Enricher should add computed fields."""
    enricher = RecordEnricher({"alpha": "type-a"})
    records = [{"id": 1, "first": "john", "last": "doe", "type": "alpha", "metrics": {"a": 10, "b": 20, "c": 30}}]
    result = enricher.enrich(records)
    assert result[0]["full_name"] == "john doe"
    assert result[0]["category"] == "type-a"
    assert "score" in result[0]


# --- Performance tests ---

def test_performance_large_pipeline():
    """Large pipeline should complete quickly without deep copy overhead."""
    pipeline = DataPipeline()
    enricher = RecordEnricher({"alpha": "type-a", "beta": "type-b", "gamma": "type-g", "delta": "type-d"})
    normalizer = Normalizer()
    pipeline.add_stage("enrich", enricher.enrich)
    pipeline.add_stage("normalize", normalizer.normalize)

    records = generate_records(5000)

    t0 = time.perf_counter()
    result = pipeline.process(records)
    elapsed = time.perf_counter() - t0

    assert len(result) == 5000
    assert elapsed < 0.3, \
        f"5000-record pipeline took {elapsed:.3f}s (should be < 0.3s, deepcopy issue?)"


def test_performance_aggregate():
    """Aggregation of large dataset should be fast."""
    enricher = RecordEnricher({"alpha": "type-a"})
    normalizer = Normalizer()
    agg = Aggregator()

    records = generate_records(5000)
    records = enricher.enrich(records)
    records = normalizer.normalize(records)

    t0 = time.perf_counter()
    result = agg.aggregate(records, "department")
    elapsed = time.perf_counter() - t0

    assert len(result) > 0
    assert elapsed < 0.2, \
        f"Aggregation took {elapsed:.3f}s (should be < 0.2s, deepcopy issue?)"