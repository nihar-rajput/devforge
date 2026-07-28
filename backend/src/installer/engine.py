"""
Core InstallationEngine orchestrator.

Coordinates dependency resolution, pipeline execution, transactions, rollback,
and database persistence.
"""

from __future__ import annotations

from pathlib import Path
from typing import List
from uuid import UUID

from src.config.settings import AppSettings
from src.core.entities.installation import Installation
from src.core.enums import InstallationStage, PackageStatus
from src.core.events.install_events import InstallationCompleted, InstallationFailed, InstallationStarted
from src.core.ports.event_bus import EventBus
from src.core.ports.installation_repository import InstallationRepository
from src.core.ports.package_repository import PackageRepository
from src.core.value_objects.package_id import PackageId
from src.dependency_resolver.resolver import DependencyResolver
from src.installer.queue_manager import InstallationQueueManager
from src.installer.rollback_manager import RollbackManager
from src.installer.step_runner import StepRunner
from src.installer.transaction import InstallationTransaction
from src.logger.structured_logger import StructuredLogger
from src.package_manager.base_plugin import InstallOptions
from src.package_manager.plugin_manager import PluginManager

logger = StructuredLogger("installer.engine")


class InstallationEngine:
    """
    Core installation engine orchestrating the complete software installation lifecycle.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        package_repo: PackageRepository | None = None,
        installation_repo: InstallationRepository | None = None,
        event_bus: EventBus | None = None,
        step_runner: StepRunner | None = None,
        rollback_manager: RollbackManager | None = None,
    ) -> None:
        settings = AppSettings()
        self._plugin_manager = plugin_manager
        self._package_repo = package_repo
        self._installation_repo = installation_repo
        self._event_bus = event_bus
        self._resolver = DependencyResolver(plugin_manager)
        self._step_runner = step_runner or StepRunner(event_bus=event_bus)
        self._rollback_manager = rollback_manager or RollbackManager(event_bus=event_bus)
        self._queue_manager = InstallationQueueManager(settings.install.max_concurrent_installs)
        self._download_dir = settings.paths.download_dir

    async def install_packages(
        self,
        target_packages: List[PackageId],
        options: InstallOptions | None = None,
    ) -> List[Installation]:
        """
        Install a list of packages and their dependencies in correct topological order.

        Args:
            target_packages: Requested packages.
            options: Installation options.

        Returns:
            List of completed Installation records.
        """
        opts = options or InstallOptions()

        # 1. Resolve installation sequence (topological sort)
        ordered_packages = self._resolver.resolve_installation_order(target_packages)
        logger.info(f"Resolved installation order: {[p.value for p in ordered_packages]}")

        installations: List[Installation] = []

        # 2. Execute installation for each package in order
        for pkg_id in ordered_packages:
            plugin = self._plugin_manager.get_plugin(pkg_id)
            if not plugin:
                logger.error(f"No plugin registered for '{pkg_id.value}'")
                continue

            ver = await plugin.get_latest_version()
            inst = Installation(package_id=pkg_id, target_version=ver)
            if self._installation_repo:
                await self._installation_repo.save(inst)

            tx = InstallationTransaction(inst)
            try:
                await self._install_single_package(tx, plugin, opts)
                inst.complete()

                if self._package_repo:
                    pkg = await self._package_repo.get_by_id(pkg_id)
                    if pkg:
                        pkg.mark_installed(ver, install_path=Path("C:/Program Files") / plugin.metadata.name)
                        await self._package_repo.save(pkg)

                if self._event_bus:
                    await self._event_bus.publish(
                        InstallationCompleted(
                            installation_id=inst.id,
                            package_id=pkg_id,
                            version=ver,
                            duration_seconds=inst.duration_seconds or 0.0,
                        )
                    )

            except Exception as exc:
                logger.error(f"Installation failed for '{pkg_id.value}': {exc}")
                inst.fail(str(exc))
                await self._rollback_manager.rollback_transaction(tx)

                if self._package_repo:
                    pkg = await self._package_repo.get_by_id(pkg_id)
                    if pkg:
                        pkg.mark_failed()
                        await self._package_repo.save(pkg)

                if self._event_bus:
                    await self._event_bus.publish(
                        InstallationFailed(
                            installation_id=inst.id,
                            package_id=pkg_id,
                            error=str(exc),
                            failed_at_stage=inst.current_stage,
                        )
                    )
                raise

            finally:
                if self._installation_repo:
                    await self._installation_repo.save(inst)
                installations.append(inst)

        return installations

    async def _install_single_package(
        self,
        tx: InstallationTransaction,
        plugin: BasePlugin,
        options: InstallOptions,
    ) -> None:
        pkg_id = plugin.metadata.id
        logger.info(f"Executing installation pipeline for '{pkg_id.value}'...")

        if self._event_bus:
            await self._event_bus.publish(
                InstallationStarted(
                    installation_id=tx.installation.id,
                    package_id=pkg_id,
                    target_version=tx.installation.target_version,
                    total_steps=4,
                )
            )

        # Stage 1: Download installer
        installer_file = await self._step_runner.execute_download_step(tx, plugin, self._download_dir)

        # Stage 2: Silent install
        await self._step_runner.execute_install_step(tx, plugin, installer_file, options)

        # Stage 3: PATH configuration
        await self._step_runner.execute_path_step(tx, plugin)

        # Stage 4: Verification
        await self._step_runner.execute_verify_step(tx, plugin)
