"""Hidden tests for t17_buffer_perf — O(n²) prepend in StringBuffer.

3 correctness tests + 2 performance tests.
Buggy: correctness=1.0, performance=0.0 → 0.6
Solution: all pass → 1.0
"""
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buffer import StringBuffer, ReportBuilder


# --- Correctness tests ---

def test_basic_buffer():
    """Basic buffer operations should work."""
    buf = StringBuffer()
    buf.append("line1")
    buf.append("line2")
    buf.prepend("header")
    assert buf.build() == "header\nline1\nline2"


def test_report_builder():
    """Report builder should produce correct output."""
    rb = ReportBuilder("Test Report")
    rb.add_header("Section 1")
    rb.add_line("Some content")
    rb.add_table(["Name", "Value"], [["A", "1"], ["B", "2"]])
    rb.add_footer("Generated automatically")
    result = rb.build()
    assert "# Test Report" in result
    assert "## Section 1" in result
    assert "| Name | Value |" in result
    assert "Generated automatically" in result


def test_prepend_order():
    """Prepended items should appear in the correct order."""
    buf = StringBuffer()
    buf.append("body")
    buf.prepend("second")
    buf.prepend("first")
    assert buf.build() == "first\nsecond\nbody"


# --- Performance tests ---

def test_performance_small():
    """Small buffer should be fast."""
    t0 = time.perf_counter()
    for _ in range(100):
        buf = StringBuffer()
        for i in range(100):
            buf.append(f"line{i}")
        buf.prepend("header")
        buf.build()
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.05, f"Too slow: {elapsed:.3f}s"


def test_performance_many_prepends():
    """Many prepends should not cause quadratic slowdown."""
    t0 = time.perf_counter()
    buf = StringBuffer()
    # Add 50000 lines and 50000 prepends
    for i in range(50000):
        buf.append(f"line-{i}")
    for i in range(50000):
        buf.prepend(f"header-{i}")
    result = buf.build()
    elapsed = time.perf_counter() - t0

    lines = result.split("\n")
    assert len(lines) == 100000, f"Expected 100000 lines, got {len(lines)}"
    assert elapsed < 0.5, \
        f"100000 operations took {elapsed:.2f}s (should be < 0.5s, O(n²) issue?)"