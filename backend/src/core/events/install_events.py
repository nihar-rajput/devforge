"""
Installation-related domain events.

Emitted by the installation engine and consumed by the WebSocket
handler for real-time step-by-step progress display.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.core.enums import EventSeverity, InstallationStage
from src.core.events.base import DomainEvent
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version


class InstallationStarted(DomainEvent):
    """Emitted when an installation pipeline begins for a package."""

    event_type: str = "InstallationStarted"
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package being installed.")
    target_version: Version = Field(..., description="Version being installed.")
    total_steps: int = Field(..., description="Total number of pipeline steps.")
    message: str = "Installation started"


class InstallationStepStarted(DomainEvent):
    """Emitted when an individual installation step begins."""

    event_type: str = "InstallationStepStarted"
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package being installed.")
    stage: InstallationStage = Field(..., description="Pipeline stage starting.")
    step_index: int = Field(..., description="Step number (0-based).")
    step_description: str = Field(..., description="What this step does.")
    message: str = "Installation step started"


class InstallationStepCompleted(DomainEvent):
    """Emitted when an individual installation step completes successfully."""

    event_type: str = "InstallationStepCompleted"
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package being installed.")
    stage: InstallationStage = Field(..., description="Pipeline stage completed.")
    step_index: int = Field(..., description="Step number (0-based).")
    duration_seconds: float = Field(..., description="Time this step took.")
    progress_percent: float = Field(..., description="Overall installation progress.")
    message: str = "Installation step completed"


class InstallationStepFailed(DomainEvent):
    """Emitted when an individual installation step fails."""

    event_type: str = "InstallationStepFailed"
    severity: EventSeverity = EventSeverity.ERROR
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package being installed.")
    stage: InstallationStage = Field(..., description="Pipeline stage that failed.")
    step_index: int = Field(..., description="Step number (0-based).")
    error: str = Field(..., description="Error description.")
    will_retry: bool = Field(..., description="Whether the step will be retried.")
    will_rollback: bool = Field(..., description="Whether a rollback will be attempted.")
    message: str = "Installation step failed"


class InstallationCompleted(DomainEvent):
    """Emitted when all installation steps complete successfully."""

    event_type: str = "InstallationCompleted"
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package installed.")
    version: Version = Field(..., description="Version installed.")
    duration_seconds: float = Field(..., description="Total installation time.")
    message: str = "Installation completed successfully"


class InstallationFailed(DomainEvent):
    """Emitted when an installation fails and cannot be recovered."""

    event_type: str = "InstallationFailed"
    severity: EventSeverity = EventSeverity.ERROR
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package that failed to install.")
    error: str = Field(..., description="Error summary.")
    failed_at_stage: InstallationStage = Field(..., description="Stage where failure occurred.")
    message: str = "Installation failed"


class InstallationRolledBack(DomainEvent):
    """Emitted when a failed installation is rolled back."""

    event_type: str = "InstallationRolledBack"
    severity: EventSeverity = EventSeverity.WARNING
    installation_id: UUID = Field(..., description="Installation operation ID.")
    package_id: PackageId = Field(..., description="Package whose install was rolled back.")
    steps_reversed: int = Field(..., description="Number of steps that were reversed.")
    message: str = "Installation rolled back"


class UninstallationStarted(DomainEvent):
    """Emitted when an uninstallation begins."""

    event_type: str = "UninstallationStarted"
    package_id: PackageId = Field(..., description="Package being uninstalled.")
    version: Version = Field(..., description="Version being removed.")
    message: str = "Uninstallation started"


class UninstallationCompleted(DomainEvent):
    """Emitted when an uninstallation completes."""

    event_type: str = "UninstallationCompleted"
    package_id: PackageId = Field(..., description="Package uninstalled.")
    duration_seconds: float = Field(..., description="Total uninstall time.")
    message: str = "Uninstallation completed"
