"""Hidden tests for t25_tree_overflow — recursive overflow on deep trees.

5 correctness tests. The buggy code uses recursion and overflows
on deep trees (depth > 900). The fix must convert to iterative
algorithms.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tree import TreeNode, build_deep_tree, tree_depth, tree_sum, count_nodes, find_node


def test_shallow_tree():
    """Shallow trees should work correctly."""
    root = build_deep_tree(5, branching=2)
    assert tree_depth(root) == 5
    assert count_nodes(root) == 31  # 2^5 - 1
    assert tree_sum(root) == 0  # all values are string "node-X"


def test_medium_tree():
    """Medium trees should work."""
    root = build_deep_tree(10, branching=1)
    assert tree_depth(root) == 10
    assert count_nodes(root) == 10


def test_single_node():
    """Single node should work."""
    root = TreeNode(42)
    assert tree_depth(root) == 1
    assert tree_sum(root) == 42
    assert count_nodes(root) == 1


def test_deep_tree():
    """Deep tree (depth 1000) should not cause RecursionError."""
    root = build_deep_tree(1000, branching=1)
    # Should not raise RecursionError
    depth = tree_depth(root)
    assert depth == 1000, f"Expected depth 1000, got {depth}"


def test_find_in_deep_tree():
    """Finding a node in a deep tree should work."""
    root = build_deep_tree(500, branching=1)
    # Build a tree with a specific node at the bottom
    leaf = root
    while leaf.children:
        leaf = leaf.children[0]
    leaf.value = "TARGET"

    found = find_node(root, lambda n: n.value == "TARGET")
    assert found is not None, "Should find TARGET node"
    assert found.value == "TARGET"