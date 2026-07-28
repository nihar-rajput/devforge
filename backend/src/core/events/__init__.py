"""Domain events for the event bus system."""

from src.core.events.base import DomainEvent
from src.core.events.download_events import (
    DownloadCancelled,
    DownloadCompleted,
    DownloadFailed,
    DownloadPaused,
    DownloadProgressUpdated,
    DownloadResumed,
    DownloadStarted,
)
from src.core.events.install_events import (
    InstallationCompleted,
    InstallationFailed,
    InstallationRolledBack,
    InstallationStarted,
    InstallationStepCompleted,
    InstallationStepFailed,
    InstallationStepStarted,
    UninstallationCompleted,
    UninstallationStarted,
)
from src.core.events.system_events import (
    EnvironmentVariableChanged,
    GPUDetected,
    HealthCheckCompleted,
    PathEntryAdded,
    PathEntryRemoved,
    SoftwareDetected,
)

__all__ = [
    "DomainEvent",
    "DownloadCancelled",
    "DownloadCompleted",
    "DownloadFailed",
    "DownloadPaused",
    "DownloadProgressUpdated",
    "DownloadResumed",
    "DownloadStarted",
    "EnvironmentVariableChanged",
    "GPUDetected",
    "HealthCheckCompleted",
    "InstallationCompleted",
    "InstallationFailed",
    "InstallationRolledBack",
    "InstallationStarted",
    "InstallationStepCompleted",
    "InstallationStepFailed",
    "InstallationStepStarted",
    "PathEntryAdded",
    "PathEntryRemoved",
    "SoftwareDetected",
    "UninstallationCompleted",
    "UninstallationStarted",
]
