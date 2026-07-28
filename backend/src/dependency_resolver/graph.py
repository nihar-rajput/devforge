"""
Dependency DAG graph builder.
"""

from __future__ import annotations

from typing import Dict, List, Set

from src.core.entities.package import Dependency
from src.core.value_objects.package_id import PackageId
from src.package_manager.plugin_manager import PluginManager


class DependencyGraph:
    """
    Builds a Directed Acyclic Graph (DAG) from package dependencies.
    """

    def __init__(self, plugin_manager: PluginManager) -> None:
        self._plugin_manager = plugin_manager

    def build_graph(self, target_packages: List[PackageId]) -> Dict[str, Set[str]]:
        """
        Build dependency graph dictionary where key is package ID string and value
        is a set of package ID strings that the key DEPENDS ON.

        Returns:
            Dict[str, Set[str]] suitable for graphlib.TopologicalSorter.
        """
        graph: Dict[str, Set[str]] = {}
        visited: Set[str] = set()

        def add_node(pkg_id: PackageId) -> None:
            key = pkg_id.value
            if key in visited:
                return
            visited.add(key)

            plugin = self._plugin_manager.get_plugin(pkg_id)
            if not plugin:
                graph[key] = set()
                return

            deps_keys: Set[str] = set()
            for dep in plugin.dependencies:
                if not dep.optional:
                    deps_keys.add(dep.package_id.value)
                    add_node(dep.package_id)

            graph[key] = deps_keys

        for pkg in target_packages:
            add_node(pkg)

        return graph
