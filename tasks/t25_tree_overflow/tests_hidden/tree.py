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
    """Calculate the maximum depth of a tree (iterative)."""
    if root is None:
        return 0
    max_depth = 0
    stack = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)
        for child in node.children:
            stack.append((child, depth + 1))
    return max_depth


def tree_sum(root):
    """Sum all values in a tree (iterative)."""
    if root is None:
        return 0
    total = 0
    stack = [root]
    while stack:
        node = stack.pop()
        if isinstance(node.value, (int, float)):
            total += node.value
        for child in node.children:
            stack.append(child)
    return total


def find_node(root, predicate):
    """Find the first node matching a predicate (iterative)."""
    if root is None:
        return None
    stack = [root]
    while stack:
        node = stack.pop()
        if predicate(node):
            return node
        for child in reversed(node.children):
            stack.append(child)
    return None


def count_nodes(root):
    """Count all nodes in the tree (iterative)."""
    if root is None:
        return 0
    count = 0
    stack = [root]
    while stack:
        node = stack.pop()
        count += 1
        for child in node.children:
            stack.append(child)
    return count