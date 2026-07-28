"""
Rollback manager for undoing completed transaction steps upon failure.
"""

from __future__ import annotations

from src.core.entities.installation import InstallationStep
from src.core.events.install_events import InstallationRolledBack
from src.core.ports.event_bus import EventBus
from src.installer.transaction import InstallationTransaction
from src.logger.structured_logger import StructuredLogger
from src.system.path_manager import WindowsPathManager

logger = StructuredLogger("installer.rollback")


class RollbackManager:
    """
    Executes reverse cleanup logic on completed step checkpoints after an installation failure.
    """

    def __init__(
        self,
        path_manager: WindowsPathManager | None = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._path_manager = path_manager or WindowsPathManager()
        self._event_bus = event_bus

    async def rollback_transaction(self, tx: InstallationTransaction) -> int:
        """
        Roll back all completed checkpoints in LIFO order.

        Returns:
            Number of steps reversed.
        """
        checkpoints = tx.completed_checkpoints
        reversed_count = 0

        logger.warning(f"Initiating rollback for installation '{tx.installation.id}' ({len(checkpoints)} steps to undo)...")

        for step in checkpoints:
            try:
                await self._rollback_step(step)
                reversed_count += 1
            except Exception as exc:
                logger.error(f"Failed to rollback step [{step.stage.value}]: {exc}")

        tx.installation.mark_rolled_back()

        if self._event_bus:
            await self._event_bus.publish(
                InstallationRolledBack(
                    installation_id=tx.installation.id,
                    package_id=tx.installation.package_id,
                    steps_reversed=reversed_count,
                )
            )

        return reversed_count

    async def _rollback_step(self, step: InstallationStep) -> None:
        if step.rollback_command == "remove_from_path":
            if step.rollback_data and "path" in step.rollback_data:
                await self._path_manager.remove_from_path(step.rollback_data["path"])
                logger.info(f"Rollback: removed PATH entry {step.rollback_data['path']}")
