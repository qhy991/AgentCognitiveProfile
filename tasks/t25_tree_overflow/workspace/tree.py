"""Tree data structure and traversal algorithms.

Provides a generic tree implementation with common traversal
and manipulation operations.
"""


class TreeNode:
    """A node in a tree structure."""

    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []

    def add_child(self, child):
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0


def build_deep_tree(depth, branching=1):
    """Build a tree with a specific depth (for testing). Iterative."""
    if depth <= 0:
        return TreeNode(f"leaf-{depth}")
    root = TreeNode(f"node-{depth}")
    stack = [(root, depth - 1)]
    while stack:
        parent, d = stack.pop()
        if d > 0:
            for i in range(branching):
                child = TreeNode(f"node-{d}")
                parent.add_child(child)
                stack.append((child, d - 1))
    return root


def tree_depth(root):
    """Calculate the maximum depth of a tree.

    BUG: Uses recursion without a depth limit. For very deep trees
    (depth > 900), this causes a RecursionError.
    """
    if root is None:
        return 0
    if root.is_leaf():
        return 1
    return 1 + max(tree_depth(child) for child in root.children)


def tree_sum(root):
    """Sum all values in a tree. Values must be numeric.

    BUG: Uses recursion. Overflows on deep trees.
    """
    if root is None:
        return 0
    total = root.value if isinstance(root.value, (int, float)) else 0
    for child in root.children:
        total += tree_sum(child)
    return total


def find_node(root, predicate):
    """Find the first node matching a predicate.

    BUG: Recursive DFS overflows on deep trees.
    """
    if root is None:
        return None
    if predicate(root):
        return root
    for child in root.children:
        result = find_node(child, predicate)
        if result:
            return result
    return None


def count_nodes(root):
    """Count all nodes in the tree.

    BUG: Recursive. Overflows on deep trees.
    """
    if root is None:
        return 0
    return 1 + sum(count_nodes(child) for child in root.children)