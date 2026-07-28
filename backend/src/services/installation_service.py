"""
Installation service implementation.
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from src.core.entities.installation import Installation
from src.core.value_objects.package_id import PackageId
from src.installer.engine import InstallationEngine
from src.installer.uninstaller import Uninstaller
from src.package_manager.base_plugin import InstallOptions
from src.package_manager.plugin_manager import PluginManager
from src.repairer.repair_engine import RepairEngine


class InstallationService:
    """
    High-level application service coordinating installation, uninstallation, and repair.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        installation_engine: InstallationEngine,
        uninstaller: Uninstaller,
        repair_engine: RepairEngine,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._engine = installation_engine
        self._uninstaller = uninstaller
        self._repair_engine = repair_engine

    async def install_stack(
        self,
        package_ids: List[PackageId],
        options: InstallOptions | None = None,
    ) -> List[Installation]:
        """
        Install a set of packages (a stack) and their dependencies.
        """
        return await self._engine.install_packages(package_ids, options)

    async def uninstall_package(self, package_id: PackageId) -> bool:
        """
        Uninstall a single package.
        """
        plugin = self._plugin_manager.get_plugin(package_id)
        if not plugin:
            return False
        return await self._uninstaller.uninstall(plugin)

    async def repair_package(self, package_id: PackageId) -> bool:
        """
        Repair a broken package installation.
        """
        return await self._repair_engine.repair_package(package_id)
