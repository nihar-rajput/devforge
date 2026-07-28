"""
Uninstaller engine implementation for clean software package removal.
"""

from __future__ import annotations

from src.core.enums import PackageStatus
from src.core.events.install_events import UninstallationCompleted, UninstallationStarted
from src.core.ports.event_bus import EventBus
from src.core.ports.package_repository import PackageRepository
from src.logger.structured_logger import StructuredLogger
from src.package_manager.base_plugin import BasePlugin, UninstallContext
from src.package_manager.plugin_manager import PluginManager
from src.system.path_manager import WindowsPathManager
from src.system.process_runner import AsyncProcessRunner

logger = StructuredLogger("installer.uninstaller")


class Uninstaller:
    """
    Orchestrates clean uninstallation of software packages.
    """

    def __init__(

        self,
        plugin_manager: PluginManager,
        package_repo: PackageRepository | None = None,
        process_runner: AsyncProcessRunner | None = None,
        path_manager: WindowsPathManager | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._package_repo = package_repo
        self._runner = process_runner or AsyncProcessRunner()
        self._path_manager = path_manager or WindowsPathManager()
        self._event_bus = event_bus

    async def uninstall(self, plugin: BasePlugin) -> bool:
        """
        Cleanly uninstall a package.
        """
        pkg_id = plugin.metadata.id
        logger.info(f"Starting uninstallation for package '{pkg_id.value}'...")

        if self._event_bus:
            await self._event_bus.publish(
                UninstallationStarted(
                    package_id=pkg_id,
                    version=plugin.metadata.id,  # Default fallback
                )
            )

        context = UninstallContext()
        await plugin.pre_uninstall(context)

        # 1. Run silent uninstall command
        cmd = plugin.get_uninstall_command()
        res = await self._runner.run(cmd)

        if not res.success:
            logger.warning(f"Uninstall command exited with code {res.return_code}: {res.stderr}")

        # 2. Remove PATH entries
        for path in plugin.get_path_entries():
            await self._path_manager.remove_from_path(str(path))

        await plugin.post_uninstall(context)

        # 3. Update database if repo provided
        if self._package_repo:
            pkg = await self._package_repo.get_by_id(pkg_id)
            if pkg:
                pkg.mark_uninstalled()
                await self._package_repo.save(pkg)

        logger.info(f"Uninstallation completed for '{pkg_id.value}'.")

        if self._event_bus:
            await self._event_bus.publish(
                UninstallationCompleted(
                    package_id=pkg_id,
                    duration_seconds=res.duration_seconds,
                )
            )

        return True
