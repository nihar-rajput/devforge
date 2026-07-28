"""
Dependency repairer implementation.
"""

from __future__ import annotations

from src.core.value_objects.package_id import PackageId
from src.package_manager.base_plugin import BasePlugin


class DependencyRepairer:
    """
    Identifies missing dependencies for a package that need re-installation.
    """

    async def get_missing_dependencies(self, plugin: BasePlugin) -> list[PackageId]:
        """
        Get list of required dependency PackageIds for plugin.
        """
        missing: list[PackageId] = []
        for dep in plugin.dependencies:
            if not dep.optional:
                missing.append(dep.package_id)
        return missing
