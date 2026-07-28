"""
UpdateEngine orchestrator implementation.
"""

from __future__ import annotations

from typing import List

from src.core.entities.installation import Installation
from src.core.value_objects.package_id import PackageId
from src.installer.engine import InstallationEngine
from src.logger.structured_logger import StructuredLogger
from src.package_manager.plugin_manager import PluginManager
from src.updater.update_checker import UpdateChecker
from src.updater.version_resolver import UpdateVersionResolver

logger = StructuredLogger("updater.engine")


class UpdateEngine:
    """
    Orchestrates automated single and batch package updates.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        installation_engine: InstallationEngine,
        update_checker: UpdateChecker | None = None,
        version_resolver: UpdateVersionResolver | None = None,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._installation_engine = installation_engine
        self._checker = update_checker or UpdateChecker(plugin_manager)
        self._resolver = version_resolver or UpdateVersionResolver(plugin_manager)

    async def update_all(self) -> List[Installation]:
        """
        Check for all available updates and execute batch installation.

        Returns:
            List of completed Installation objects for updated packages.
        """
        logger.info("Checking for system-wide package updates...")
        updates = await self._checker.check_updates()

        if not updates:
            logger.info("All installed packages are up to date.")
            return []

        packages_to_update: List[PackageId] = []
        for pkg_str, new_ver in updates.items():
            pkg_id = PackageId.of(pkg_str)
            if await self._resolver.can_update(pkg_id, new_ver):
                packages_to_update.append(pkg_id)

        if not packages_to_update:
            logger.warning("Updates available, but skipped due to version constraint conflicts.")
            return []

        logger.info(f"Updating {len(packages_to_update)} packages: {[p.value for p in packages_to_update]}")
        return await self._installation_engine.install_packages(packages_to_update)
