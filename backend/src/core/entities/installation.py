"""
Installation entity.

Represents a single installation operation — the full pipeline from
download through verification. Each step is tracked as an InstallationStep
for audit trail, rollback, and resume capabilities.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core.enums import InstallationStage
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version


class InstallationStep(BaseModel):
    """
    A single discrete step within an installation pipeline.

    Each step is logged as a transaction checkpoint. On failure,
    the rollback manager reverses completed steps in LIFO order.
    """

    stage: InstallationStage = Field(..., description="Which pipeline stage this step belongs to.")
    message: str = Field(..., description="Human-readable description of this step.")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this step started.",
    )
    completed_at: datetime | None = Field(
        default=None, description="When this step completed (None if still running)."
    )
    success: bool | None = Field(
        default=None, description="True if step succeeded, False if failed, None if pending."
    )
    error_message: str | None = Field(
        default=None, description="Error details if the step failed."
    )
    rollback_command: str | None = Field(
        default=None,
        description="Command to undo this step (e.g., 'remove PATH entry X').",
    )
    rollback_data: dict[str, str] | None = Field(
        default=None,
        description="Structured data needed for rollback (e.g., original PATH value).",
    )

    @property
    def is_completed(self) -> bool:
        """Check if this step has finished (successfully or not)."""
        return self.success is not None

    @property
    def duration_seconds(self) -> float | None:
        """Elapsed time for this step, or None if not completed."""
        if self.completed_at is None:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    def mark_success(self, message: str | None = None) -> None:
        """Mark this step as successfully completed."""
        self.success = True
        self.completed_at = datetime.now(timezone.utc)
        if message:
            self.message = message

    def mark_failure(self, error: str) -> None:
        """Mark this step as failed."""
        self.success = False
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = error


class Installation(BaseModel):
    """
    An installation operation tracking the full lifecycle of
    installing (or uninstalling/repairing/updating) a package.

    Each installation gets a unique ID and maintains an ordered list
    of steps for auditing and rollback. The installation entity is
    persisted to the database for the history timeline.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique installation operation ID.")
    package_id: PackageId = Field(..., description="Package being installed.")
    target_version: Version = Field(..., description="Version being installed.")
    previous_version: Version | None = Field(
        default=None,
        description="Previously installed version (for updates/reinstalls).",
    )
    current_stage: InstallationStage = Field(
        default=InstallationStage.QUEUED,
        description="Current pipeline stage.",
    )
    steps: list[InstallationStep] = Field(
        default_factory=list,
        description="Ordered list of completed and pending steps.",
    )
    progress_percent: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall progress percentage.",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the installation was initiated.",
    )
    completed_at: datetime | None = Field(
        default=None, description="When the installation finished."
    )
    is_cancelled: bool = Field(
        default=False, description="Whether the user cancelled this installation."
    )
    error_summary: str | None = Field(
        default=None, description="Summary of the failure if installation failed."
    )

    @property
    def is_active(self) -> bool:
        """Check if this installation is still in progress."""
        return self.current_stage not in {
            InstallationStage.COMPLETED,
            InstallationStage.FAILED,
            InstallationStage.ROLLED_BACK,
        }

    @property
    def is_successful(self) -> bool:
        """Check if this installation completed successfully."""
        return self.current_stage == InstallationStage.COMPLETED

    @property
    def duration_seconds(self) -> float | None:
        """Total elapsed time, or None if not completed."""
        if self.completed_at is None:
            return None
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def failed_steps(self) -> list[InstallationStep]:
        """Get all steps that failed."""
        return [step for step in self.steps if step.success is False]

    @property
    def completed_steps(self) -> list[InstallationStep]:
        """Get all steps that completed successfully (for rollback ordering)."""
        return [step for step in self.steps if step.success is True]

    def add_step(
        self,
        stage: InstallationStage,
        message: str,
        rollback_command: str | None = None,
        rollback_data: dict[str, str] | None = None,
    ) -> InstallationStep:
        """
        Begin a new installation step.

        Args:
            stage: Pipeline stage this step belongs to.
            message: Human-readable description.
            rollback_command: Optional command to undo this step.
            rollback_data: Optional data needed for rollback.

        Returns:
            The newly created step (mutable, call mark_success/mark_failure on it).
        """
        step = InstallationStep(
            stage=stage,
            message=message,
            rollback_command=rollback_command,
            rollback_data=rollback_data,
        )
        self.steps.append(step)
        self.current_stage = stage
        return step

    def complete(self) -> None:
        """Mark the entire installation as completed successfully."""
        self.current_stage = InstallationStage.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.progress_percent = 100.0

    def fail(self, error_summary: str) -> None:
        """Mark the entire installation as failed."""
        self.current_stage = InstallationStage.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error_summary = error_summary

    def mark_rolled_back(self) -> None:
        """Mark the installation as rolled back after failure."""
        self.current_stage = InstallationStage.ROLLED_BACK
        self.completed_at = datetime.now(timezone.utc)
