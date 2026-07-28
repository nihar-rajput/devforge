"""
Step runner for executing individual installation pipeline stages.
"""

from __future__ import annotations

from pathlib import Path

from src.core.entities.download import Download
from src.core.enums import InstallationStage
from src.core.events.install_events import InstallationStepCompleted, InstallationStepStarted
from src.core.ports.event_bus import EventBus
from src.downloader.manager import DefaultDownloadManager
from src.installer.transaction import InstallationTransaction
from src.logger.structured_logger import StructuredLogger
from src.package_manager.base_plugin import BasePlugin, InstallContext, InstallOptions
from src.system.path_manager import WindowsPathManager
from src.system.process_runner import AsyncProcessRunner

logger = StructuredLogger("installer.step_runner")


class StepRunner:
    """
    Executes specific installation steps for a package plugin.
    """

    def __init__(
        self,
        downloader: DefaultDownloadManager | None = None,
        process_runner: AsyncProcessRunner | None = None,
        path_manager: WindowsPathManager | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._downloader = downloader or DefaultDownloadManager()
        self._runner = process_runner or AsyncProcessRunner()
        self._path_manager = path_manager or WindowsPathManager()
        self._event_bus = event_bus

    async def execute_download_step(
        self,
        tx: InstallationTransaction,
        plugin: BasePlugin,
        download_dir: Path,
    ) -> Path:
        step = tx.checkpoint(InstallationStage.DOWNLOADING, "Downloading installer binary...")
        if self._event_bus:
            await self._event_bus.publish(
                InstallationStepStarted(
                    installation_id=tx.installation.id,
                    package_id=plugin.metadata.id,
                    stage=InstallationStage.DOWNLOADING,
                    step_index=len(tx.installation.steps) - 1,
                    step_description="Downloading installer binary",
                )
            )

        ver = await plugin.get_latest_version()
        info = await plugin.get_download_info(ver)

        download = Download(
            package_id=plugin.metadata.id,
            url=info.url,
            file_name=info.file_name,
            total_size=info.file_size,
            expected_checksum=info.checksum,
        )

        destination = download_dir / info.file_name
        await self._downloader.start_download(download, destination)

        tx.mark_step_success(step)
        if self._event_bus:
            await self._event_bus.publish(
                InstallationStepCompleted(
                    installation_id=tx.installation.id,
                    package_id=plugin.metadata.id,
                    stage=InstallationStage.DOWNLOADING,
                    step_index=len(tx.installation.steps) - 1,
                    duration_seconds=step.duration_seconds or 0.0,
                    progress_percent=30.0,
                )
            )

        return destination

    async def execute_install_step(
        self,
        tx: InstallationTransaction,
        plugin: BasePlugin,
        installer_path: Path,
        options: InstallOptions,
    ) -> None:
        step = tx.checkpoint(
            InstallationStage.INSTALLING,
            f"Running silent installer for {plugin.metadata.name}...",
        )

        ver = await plugin.get_latest_version()
        context = InstallContext(installer_path=installer_path, version=ver, options=options)

        await plugin.pre_install(context)

        cmd = plugin.get_install_command(installer_path, options)
        res = await self._runner.run(cmd)

        if not res.success:
            err_msg = res.stderr or f"Exit code {res.return_code}"
            tx.mark_step_failed(step, err_msg)
            raise ValueError(f"Silent installer failed for {plugin.metadata.name}: {err_msg}")

        await plugin.post_install(context)

        tx.mark_step_success(step)

    async def execute_path_step(
        self,
        tx: InstallationTransaction,
        plugin: BasePlugin,
    ) -> None:
        paths = plugin.get_path_entries()
        if not paths:
            return

        step = tx.checkpoint(
            InstallationStage.CONFIGURING_PATH,
            "Updating system PATH environment variable...",
            rollback_command="remove_from_path",
        )

        for p in paths:
            path_str = str(p)
            await self._path_manager.add_to_path(path_str, scope="user")

        tx.mark_step_success(step)

    async def execute_verify_step(
        self,
        tx: InstallationTransaction,
        plugin: BasePlugin,
    ) -> bool:
        step = tx.checkpoint(
            InstallationStage.VERIFYING,
            "Verifying installation commands...",
        )

        ver_cmds = plugin.get_verify_commands()
        for v_cmd in ver_cmds:
            success = await self._runner.verify_installation(v_cmd)
            if not success:
                tx.mark_step_failed(step, f"Verification failed for: {v_cmd.command}")
                return False

        tx.mark_step_success(step)
        return True
