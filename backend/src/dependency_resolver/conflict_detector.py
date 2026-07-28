"""
Conflict detector for dependency resolution.
"""

from __future__ import annotations

from typing import Dict, List, Set

from src.core.errors.dependency_errors import CircularDependencyError, DependencyConflictError
from src.core.value_objects.package_id import PackageId


class ConflictDetector:
    """
    Detects circular dependencies and version constraint conflicts.
    """

    def detect_cycles(self, graph: Dict[str, Set[str]]) -> List[str] | None:
        """
        Detect circular dependencies using Tarjan / Depth First Search.

        Returns:
            List of package IDs forming the cycle if detected, or None.
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> List[str] | None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    res = dfs(neighbor)
                    if res:
                        return res
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        for node in graph:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle

        return None

    def validate_graph(self, graph: Dict[str, Set[str]]) -> None:
        """
        Validate graph for circular dependencies.

        Raises:
            CircularDependencyError: If a cycle is found.
        """
        cycle = self.detect_cycles(graph)
        if cycle:
            raise CircularDependencyError(cycle=cycle)
