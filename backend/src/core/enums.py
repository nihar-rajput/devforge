"""
Domain enumerations for DevForge.

All enumerations used across the domain model are defined here to provide
a single source of truth for valid states, categories, and types.
"""

from enum import StrEnum, unique


@unique
class PackageStatus(StrEnum):
    """Lifecycle status of a managed package."""

    AVAILABLE = "available"
    """Package exists in the catalog but is not installed."""

    DOWNLOADING = "downloading"
    """Package installer is being downloaded."""

    INSTALLING = "installing"
    """Package installation is in progress."""

    INSTALLED = "installed"
    """Package is installed and verified."""

    UPDATING = "updating"
    """Package is being updated to a newer version."""

    REPAIRING = "repairing"
    """Package installation is being repaired."""

    UNINSTALLING = "uninstalling"
    """Package is being removed."""

    FAILED = "failed"
    """Last operation on this package failed."""

    BROKEN = "broken"
    """Package is installed but health check failed."""


@unique
class InstallerType(StrEnum):
    """Type of installer binary a package uses."""

    EXE = "exe"
    """Standard Windows executable installer."""

    MSI = "msi"
    """Microsoft Installer package."""

    ZIP = "zip"
    """ZIP archive (extract-and-configure)."""

    MSIX = "msix"
    """Modern Windows MSIX package."""

    PORTABLE = "portable"
    """Portable application (no installation, just extract)."""

    CUSTOM = "custom"
    """Custom installation script or procedure."""


@unique
class Category(StrEnum):
    """Package category for organization and filtering."""

    LANGUAGE = "language"
    EDITOR = "editor"
    DATABASE = "database"
    DEVOPS = "devops"
    AI = "ai"
    UTILITY = "utility"
    RUNTIME = "runtime"
    BUILD_TOOL = "build_tool"
    VERSION_CONTROL = "version_control"
    FRAMEWORK = "framework"


@unique
class DownloadStatus(StrEnum):
    """Status of a download task."""

    PENDING = "pending"
    """Download is queued but not started."""

    IN_PROGRESS = "in_progress"
    """Download is actively transferring data."""

    PAUSED = "paused"
    """Download is paused by user or system."""

    COMPLETED = "completed"
    """Download finished successfully and checksum verified."""

    FAILED = "failed"
    """Download failed after exhausting retries."""

    CANCELLED = "cancelled"
    """Download was cancelled by the user."""

    CACHED = "cached"
    """File already exists in cache with valid checksum."""


@unique
class InstallationStage(StrEnum):
    """Discrete stages within an installation pipeline."""

    QUEUED = "queued"
    """Installation is queued, waiting for its turn."""

    RESOLVING_DEPENDENCIES = "resolving_dependencies"
    """Computing dependency graph and installation order."""

    DOWNLOADING = "downloading"
    """Downloading the installer binary."""

    VERIFYING_CHECKSUM = "verifying_checksum"
    """Verifying downloaded file integrity."""

    EXTRACTING = "extracting"
    """Extracting archive (ZIP/portable only)."""

    INSTALLING = "installing"
    """Running the silent installer."""

    CONFIGURING_PATH = "configuring_path"
    """Updating PATH environment variable."""

    CONFIGURING_ENV = "configuring_env"
    """Setting additional environment variables."""

    INSTALLING_DEPENDENCIES = "installing_dependencies"
    """Installing post-install dependencies (e.g., pip packages)."""

    VERIFYING = "verifying"
    """Running verification commands to confirm success."""

    COMPLETED = "completed"
    """All stages finished successfully."""

    FAILED = "failed"
    """Installation failed at some stage."""

    ROLLED_BACK = "rolled_back"
    """Installation was rolled back after failure."""


@unique
class HealthStatus(StrEnum):
    """Overall health assessment of a package installation."""

    HEALTHY = "healthy"
    """All checks pass, score ≥ 80."""

    DEGRADED = "degraded"
    """Some checks fail, score 40-79."""

    UNHEALTHY = "unhealthy"
    """Critical checks fail, score < 40."""

    UNKNOWN = "unknown"
    """Health has not been assessed yet."""


@unique
class GPUVendor(StrEnum):
    """GPU hardware vendor."""

    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    NONE = "none"


@unique
class Architecture(StrEnum):
    """System CPU architecture."""

    X86_64 = "x86_64"
    ARM64 = "arm64"


@unique
class EventSeverity(StrEnum):
    """Severity level for system events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@unique
class UpdateStrategy(StrEnum):
    """How a package should be updated."""

    IN_PLACE = "in_place"
    """Run the new installer over the existing installation."""

    UNINSTALL_REINSTALL = "uninstall_reinstall"
    """Remove old version, then install new version."""

    SIDE_BY_SIDE = "side_by_side"
    """Install new version alongside old (e.g., Python 3.12 + 3.13)."""
