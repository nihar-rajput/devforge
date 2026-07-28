"""
System-level domain events.

Emitted by detection, repair, and system integration components
when changes are made to the Windows environment.
"""

from __future__ import annotations

from pydantic import Field

from src.core.enums import EventSeverity, GPUVendor, HealthStatus
from src.core.events.base import DomainEvent
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version


class SoftwareDetected(DomainEvent):
    """Emitted when the detection engine finds installed software."""

    event_type: str = "SoftwareDetected"
    package_id: PackageId = Field(..., description="Detected package.")
    detected_version: Version = Field(..., description="Detected version.")
    install_path: str = Field(..., description="Detected installation path.")
    detection_method: str = Field(
        ..., description="How it was detected (registry, PATH, filesystem)."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence (0.0-1.0).",
    )
    message: str = "Software detected"


class GPUDetected(DomainEvent):
    """Emitted when GPU hardware is detected."""

    event_type: str = "GPUDetected"
    vendor: GPUVendor = Field(..., description="GPU vendor.")
    device_name: str = Field(..., description="GPU device name.")
    driver_version: str | None = Field(default=None, description="Driver version.")
    vram_mb: int | None = Field(default=None, description="VRAM in megabytes.")
    cuda_version: str | None = Field(default=None, description="CUDA version if NVIDIA.")
    compute_capability: str | None = Field(
        default=None, description="CUDA compute capability (e.g., '8.9')."
    )
    message: str = "GPU detected"


class PathEntryAdded(DomainEvent):
    """Emitted when a PATH entry is added to the system."""

    event_type: str = "PathEntryAdded"
    path_entry: str = Field(..., description="PATH entry that was added.")
    scope: str = Field(..., description="'user' or 'system' scope.")
    package_id: PackageId | None = Field(
        default=None, description="Package that requested this change."
    )
    message: str = "PATH entry added"


class PathEntryRemoved(DomainEvent):
    """Emitted when a PATH entry is removed from the system."""

    event_type: str = "PathEntryRemoved"
    severity: EventSeverity = EventSeverity.WARNING
    path_entry: str = Field(..., description="PATH entry that was removed.")
    scope: str = Field(..., description="'user' or 'system' scope.")
    package_id: PackageId | None = Field(
        default=None, description="Package that requested this change."
    )
    message: str = "PATH entry removed"


class EnvironmentVariableChanged(DomainEvent):
    """Emitted when an environment variable is created or modified."""

    event_type: str = "EnvironmentVariableChanged"
    variable_name: str = Field(..., description="Name of the environment variable.")
    new_value: str = Field(..., description="New value set.")
    previous_value: str | None = Field(default=None, description="Previous value, if any.")
    scope: str = Field(..., description="'user' or 'system' scope.")
    package_id: PackageId | None = Field(
        default=None, description="Package that requested this change."
    )
    message: str = "Environment variable changed"


class HealthCheckCompleted(DomainEvent):
    """Emitted when a health check finishes for a package."""

    event_type: str = "HealthCheckCompleted"
    package_id: PackageId = Field(..., description="Package checked.")
    score: int = Field(..., ge=0, le=100, description="Health score 0-100.")
    status: HealthStatus = Field(..., description="Health status category.")
    checks_passed: int = Field(..., description="Number of checks that passed.")
    checks_total: int = Field(..., description="Total number of checks run.")
    message: str = "Health check completed"
