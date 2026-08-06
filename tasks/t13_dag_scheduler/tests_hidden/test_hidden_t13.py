"""Hidden tests for t13_dag_scheduler — DAG topological sort.

The bug: Kahn's algorithm with regular queue does NOT guarantee that
a node's dependencies are ordered correctly when the graph has diamond
dependencies. The issue is that `get_levels()` uses the topological sort
order to compute levels, but if a node is at the wrong level, it may
execute before all its dependencies are marked complete.

We test: the topological order always respects ALL dependency edges.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dag import DAG


def test_simple_linear_chain():
    """A → B → C: order must be [A, B, C]."""
    dag = DAG()
    dag.add_node("A")
    dag.add_node("B")
    dag.add_node("C")
    dag.add_edge("A", "B")
    dag.add_edge("B", "C")
    order = dag.topological_sort()
    assert order.index("A") < order.index("B") < order.index("C"), \
        f"linear chain order wrong: {order}"


def test_diamond_dependency():
    """Diamond: A→B, A→C, B→D, C→D. D must come after both B and C."""
    dag = DAG()
    for n in ["A", "B", "C", "D"]:
        dag.add_node(n)
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("C", "D")
    order = dag.topological_sort()
    assert order.index("A") < order.index("B"), f"diamond: A before B, got {order}"
    assert order.index("A") < order.index("C"), f"diamond: A before C, got {order}"
    assert order.index("B") < order.index("D"), f"diamond: B before D, got {order}"
    assert order.index("C") < order.index("D"), f"diamond: C before D, got {order}"


def test_complex_dag():
    """Multiple dependency levels: A→B, A→C, B→D, C→D, D→E, B→E."""
    dag = DAG()
    for n in ["A", "B", "C", "D", "E"]:
        dag.add_node(n)
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("C", "D")
    dag.add_edge("D", "E")
    dag.add_edge("B", "E")
    order = dag.topological_sort()
    # All dependencies must be respected
    assert order.index("A") < order.index("B")
    assert order.index("A") < order.index("C")
    assert order.index("B") < order.index("D")
    assert order.index("C") < order.index("D")
    assert order.index("D") < order.index("E")
    assert order.index("B") < order.index("E")


def test_levels_diamond():
    """Diamond levels: A=0, B=1, C=1, D=2."""
    dag = DAG()
    for n in ["A", "B", "C", "D"]:
        dag.add_node(n)
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("C", "D")
    levels = dag.get_levels()
    assert levels["A"] == 0, f"expected A at level 0, got {levels}"
    assert levels["B"] == 1, f"expected B at level 1, got {levels}"
    assert levels["C"] == 1, f"expected C at level 1, got {levels}"
    assert levels["D"] == 2, f"expected D at level 2, got {levels}"


def test_cycle_detection():
    """Adding a cycle should raise an error."""
    dag = DAG()
    dag.add_node("A")
    dag.add_node("B")
    dag.add_edge("A", "B")
    dag.add_edge("B", "A")  # cycle
    try:
        dag.topological_sort()
        assert False, "should have raised ValueError for cycle"
    except ValueError:
        pass