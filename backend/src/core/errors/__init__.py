"""Domain error types."""

from src.core.errors.base import DevForgeError
from src.core.errors.dependency_errors import (
    CircularDependencyError,
    DependencyConflictError,
    DependencyResolutionError,
    UnsatisfiedDependencyError,
)
from src.core.errors.detection_errors import (
    DetectionError,
    DetectionTimeoutError,
    GPUDetectionError,
)
from src.core.errors.download_errors import (
    ChecksumMismatchError,
    DownloadError,
    DownloadResumeError,
    DownloadTimeoutError,
)
from src.core.errors.install_errors import (
    InstallationError,
    InstallerExecutionError,
    RollbackError,
    UninstallationError,
)

__all__ = [
    "ChecksumMismatchError",
    "CircularDependencyError",
    "DependencyConflictError",
    "DependencyResolutionError",
    "DetectionError",
    "DetectionTimeoutError",
    "DevForgeError",
    "DownloadError",
    "DownloadResumeError",
    "DownloadTimeoutError",
    "GPUDetectionError",
    "InstallationError",
    "InstallerExecutionError",
    "RollbackError",
    "UninstallationError",
    "UnsatisfiedDependencyError",
]
