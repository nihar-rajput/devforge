"""
Dependency resolver implementation using graphlib.TopologicalSorter.
"""

from __future__ import annotations

from graphlib import CycleError, TopologicalSorter
from typing import List

from src.core.errors.dependency_errors import CircularDependencyError
from src.core.value_objects.package_id import PackageId
from src.dependency_resolver.conflict_detector import ConflictDetector
from src.dependency_resolver.graph import DependencyGraph
from src.package_manager.plugin_manager import PluginManager


class DependencyResolver:
    """
    Computes valid installation sequence using topological sorting.
    """

    def __init__(self, plugin_manager: PluginManager) -> None:
        self._plugin_manager = plugin_manager
        self._graph_builder = DependencyGraph(plugin_manager)
        self._conflict_detector = ConflictDetector()

    def resolve_installation_order(self, target_packages: List[PackageId]) -> List[PackageId]:
        """
        Compute ordered list of PackageIds to install (dependencies first).

        Args:
            target_packages: List of packages requested for installation.

        Returns:
            Ordered list of PackageIds in installation sequence.

        Raises:
            CircularDependencyError: If a cycle is detected in dependencies.
        """
        graph = self._graph_builder.build_graph(target_packages)

        # Validate for cycles using our conflict detector first
        self._conflict_detector.validate_graph(graph)

        # Use Python stdlib TopologicalSorter
        # graph is dict: node -> dependencies (node depends on items in set)
        try:
            ts = TopologicalSorter(graph)
            ordered_strings = list(ts.static_order())
        except CycleError as exc:
            cycle_nodes = list(exc.args[1]) if len(exc.args) > 1 else []
            raise CircularDependencyError(cycle=cycle_nodes) from exc

        return [PackageId.of(s) for s in ordered_strings]
