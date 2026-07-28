"""
Installation transaction context with checkpoint logging.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from src.core.entities.installation import Installation, InstallationStep
from src.core.enums import InstallationStage
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("installer.transaction")


class InstallationTransaction:
    """
    Manages transactional checkpoints during an installation operation.
    Enables atomic operations and structured rollback.
    """

    def __init__(self, installation: Installation) -> None:
        self.installation = installation
        self._checkpoints: List[InstallationStep] = []

    def checkpoint(
        self,
        stage: InstallationStage,
        message: str,
        rollback_command: str | None = None,
        rollback_data: Dict[str, Any] | None = None,
    ) -> InstallationStep:
        """
        Record a new transaction step checkpoint.
        """
        step = self.installation.add_step(
            stage=stage,
            message=message,
            rollback_command=rollback_command,
            rollback_data=rollback_data,
        )
        self._checkpoints.append(step)
        logger.info(f"Transaction checkpoint [{stage.value}]: {message}")
        return step

    def mark_step_success(self, step: InstallationStep) -> None:
        step.mark_success()
        logger.info(f"Transaction step completed [{step.stage.value}]")

    def mark_step_failed(self, step: InstallationStep, error: str) -> None:
        step.mark_failure(error)
        logger.error(f"Transaction step failed [{step.stage.value}]: {error}")

    @property
    def completed_checkpoints(self) -> List[InstallationStep]:
        """Get checkpoints in reverse chronological order for rollback."""
        return [step for step in reversed(self._checkpoints) if step.success is True]
