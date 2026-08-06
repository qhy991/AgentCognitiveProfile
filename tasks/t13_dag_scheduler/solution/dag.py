"""Directed Acyclic Graph — stores nodes and edges, computes topological order."""

from collections import deque


class DAG:
    """A directed acyclic graph for task dependency resolution.

    Detects cycles and computes a topological ordering.
    """

    def __init__(self):
        self._nodes = set()
        self._edges = {}  # {from_node: set(to_nodes)}
        self._in_degree = {}  # {node: count}

    def add_node(self, name):
        """Add a node to the graph."""
        self._nodes.add(name)
        if name not in self._edges:
            self._edges[name] = set()
        if name not in self._in_degree:
            self._in_degree[name] = 0

    def add_edge(self, from_node, to_node):
        """Add a directed edge: from_node → to_node."""
        assert from_node in self._nodes, f"unknown node: {from_node}"
        assert to_node in self._nodes, f"unknown node: {to_node}"
        if to_node not in self._edges[from_node]:
            self._edges[from_node].add(to_node)
            self._in_degree[to_node] += 1

    def topological_sort(self):
        """Return nodes in topological order using Kahn's algorithm.

        The result should be a valid execution order where all dependencies
        of a node appear before it.
        """
        in_degree = dict(self._in_degree)

        # Initialize queue with nodes that have no dependencies
        queue = deque([n for n in self._nodes if in_degree[n] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in self._edges.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self._nodes):
            raise ValueError("Cycle detected in task dependencies")

        return result

    def get_levels(self):
        """Return nodes grouped by level (distance from source nodes).

        Level 0: no dependencies
        Level 1: depends only on level 0
        Level 2: depends on level 0 or 1, at least one level 1
        etc.
        """
        order = self.topological_sort()
        levels = {}
        for node in order:
            incoming = [n for n in self._nodes
                        if node in self._edges.get(n, set())]
            if not incoming:
                levels[node] = 0
            else:
                levels[node] = 1 + max(levels.get(dep, 0) for dep in incoming)
        return levels