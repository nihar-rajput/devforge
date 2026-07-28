"""
Update checker implementation.
"""

from __future__ import annotations

from typing import Dict, List

from src.core.entities.package import Package
from src.core.ports.package_repository import PackageRepository
from src.core.value_objects.version import Version
from src.logger.structured_logger import StructuredLogger
from src.package_manager.plugin_manager import PluginManager

logger = StructuredLogger("updater.checker")


class UpdateChecker:
    """
    Queries vendor endpoints via plugins to discover available software updates.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        package_repo: PackageRepository | None = None,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._package_repo = package_repo

    async def check_updates(self) -> Dict[str, Version]:
        """
        Check for available updates across all registered plugins.

        Returns:
            Dict mapping package ID string to latest available Version.
        """
        updates: Dict[str, Version] = {}
        plugins = self._plugin_manager.get_all_plugins()

        for plugin in plugins:
            try:
                pkg_id = plugin.metadata.id
                latest = await plugin.get_latest_version()

                if self._package_repo:
                    pkg = await self._package_repo.get_by_id(pkg_id)
                    if pkg and pkg.installed_version and latest > pkg.installed_version:
                        pkg.latest_version = latest
                        await self._package_repo.save(pkg)
                        updates[pkg_id.value] = latest
                else:
                    updates[pkg_id.value] = latest

            except Exception as exc:
                logger.debug(f"Failed to check updates for '{plugin.metadata.id.value}': {exc}")

        return updates
