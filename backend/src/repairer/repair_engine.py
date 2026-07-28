"""
RepairEngine orchestrator implementation.
"""

from __future__ import annotations

from src.core.entities.health_report import HealthReport
from src.core.enums import PackageStatus
from src.core.ports.package_repository import PackageRepository
from src.core.value_objects.package_id import PackageId
from src.logger.structured_logger import StructuredLogger
from src.package_manager.plugin_manager import PluginManager
from src.repairer.integrity_checker import IntegrityChecker
from src.repairer.path_repairer import PathRepairer

logger = StructuredLogger("repairer.engine")


class RepairEngine:
    """
    Automated one-click repair orchestrator.
    Diagnoses package health failures and executes appropriate repair procedures.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        package_repo: PackageRepository | None = None,
        path_repairer: PathRepairer | None = None,
        integrity_checker: IntegrityChecker | None = None,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._package_repo = package_repo
        self._path_repairer = path_repairer or PathRepairer()
        self._integrity_checker = integrity_checker or IntegrityChecker()

    async def repair_package(self, package_id: PackageId) -> bool:
        """
        Execute automated repair on a package.

        1. Fix PATH entries
        2. Run health check
        3. Update package status in repository
        """
        plugin = self._plugin_manager.get_plugin(package_id)
        if not plugin:
            logger.error(f"Cannot repair '{package_id.value}': plugin not found.")
            return False

        logger.info(f"Initiating repair for package '{package_id.value}'...")

        # 1. Repair PATH entries
        restored = await self._path_repairer.repair_path(plugin)
        if restored > 0:
            logger.info(f"Restored {restored} PATH entries for '{package_id.value}'.")

        # 2. Check health
        health = await plugin.health_check()

        # 3. Update database
        if self._package_repo:
            pkg = await self._package_repo.get_by_id(package_id)
            if pkg:
                pkg.update_health(health.overall_score)
                if health.overall_score >= 80:
                    pkg.status = PackageStatus.INSTALLED
                await self._package_repo.save(pkg)

        logger.info(f"Repair finished for '{package_id.value}'. Final health score: {health.overall_score}")
        return health.overall_score >= 80
