"""
Version resolver for update compatibility checking.
"""

from __future__ import annotations

from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.package_manager.plugin_manager import PluginManager


class UpdateVersionResolver:
    """
    Validates that updating a package respects version constraints of dependent packages.
    """

    def __init__(self, plugin_manager: PluginManager) -> None:
        self._plugin_manager = plugin_manager

    async def can_update(self, package_id: PackageId, new_version: Version) -> bool:
        """
        Check if updating package_id to new_version satisfies all dependent requirements.
        """
        all_plugins = self._plugin_manager.get_all_plugins()

        for plugin in all_plugins:
            for dep in plugin.dependencies:
                if dep.package_id == package_id:
                    if not dep.is_satisfied_by(new_version):
                        return False

        return True
