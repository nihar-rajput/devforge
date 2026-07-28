"""
Package entity and related types.

The Package entity represents a software package in the DevForge catalog.
It holds all metadata needed to download, install, verify, and manage
a piece of software.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from src.core.enums import (
    Category,
    InstallerType,
    PackageStatus,
    UpdateStrategy,
)
from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.system_requirements import SystemRequirements
from src.core.value_objects.version import Version


class PluginMetadata(BaseModel):
    """
    Identity and display information for a package plugin.

    This is what users see in the catalog and search results.
    """

    id: PackageId = Field(..., description="Unique package identifier.")
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name.")
    description: str = Field(
        ..., min_length=1, max_length=500, description="Short description of the package."
    )
    category: Category = Field(..., description="Package category for filtering.")
    icon: str | None = Field(default=None, description="Icon filename or URL.")
    website: str | None = Field(default=None, description="Official website URL.")
    documentation_url: str | None = Field(default=None, description="Documentation URL.")


class Dependency(BaseModel):
    """
    A dependency relationship between packages.

    Specifies that a package depends on another package,
    optionally with version constraints.
    """

    package_id: PackageId = Field(..., description="ID of the required package.")
    version_constraint: str | None = Field(
        default=None,
        description="Version constraint (e.g., '>=3.10.0', '~=2.0.0'). None means any version.",
    )
    optional: bool = Field(
        default=False,
        description="If True, installation proceeds even if this dependency is missing.",
    )
    reason: str | None = Field(
        default=None,
        description="Human-readable reason for this dependency.",
    )

    def is_satisfied_by(self, installed_version: Version) -> bool:
        """Check if an installed version satisfies this dependency's constraint."""
        if self.version_constraint is None:
            return True
        return installed_version.is_compatible_with(self.version_constraint)


class DownloadInfo(BaseModel):
    """
    Information needed to download a specific version of a package.

    Provided by the plugin's `get_download_info()` method.
    """

    url: str = Field(..., description="Direct download URL.")
    file_name: str = Field(..., description="Expected filename of the downloaded file.")
    file_size: FileSize | None = Field(
        default=None, description="Expected file size (for progress tracking)."
    )
    checksum: Checksum | None = Field(
        default=None, description="Expected checksum for integrity verification."
    )
    installer_type: InstallerType = Field(
        default=InstallerType.EXE, description="Type of installer file."
    )
    mirrors: list[str] = Field(
        default_factory=list,
        description="Alternative download URLs (fallback mirrors).",
    )


class Package(BaseModel):
    """
    Core domain entity representing a managed software package.

    A Package aggregates all the information DevForge needs to manage
    the full lifecycle of a software package: catalog info, install state,
    version tracking, and health status.

    This is the central entity of the domain. It is identified by its
    PackageId and transitions through PackageStatus states.
    """

    id: PackageId = Field(..., description="Unique package identifier.")
    metadata: PluginMetadata = Field(..., description="Display and catalog information.")
    status: PackageStatus = Field(
        default=PackageStatus.AVAILABLE,
        description="Current lifecycle status.",
    )
    installed_version: Version | None = Field(
        default=None, description="Currently installed version, if any."
    )
    latest_version: Version | None = Field(
        default=None, description="Latest available version from the vendor."
    )
    install_path: Path | None = Field(
        default=None, description="Filesystem path where the package is installed."
    )
    dependencies: list[Dependency] = Field(
        default_factory=list, description="Packages this package depends on."
    )
    system_requirements: SystemRequirements = Field(
        default_factory=SystemRequirements,
        description="Hardware/OS requirements.",
    )
    update_strategy: UpdateStrategy = Field(
        default=UpdateStrategy.IN_PLACE,
        description="How this package should be updated.",
    )
    health_score: int = Field(
        default=-1,
        ge=-1,
        le=100,
        description="Health score 0-100, or -1 if not assessed.",
    )
    installed_at: datetime | None = Field(
        default=None, description="Timestamp of last installation."
    )
    last_verified_at: datetime | None = Field(
        default=None, description="Timestamp of last health verification."
    )
    last_updated_at: datetime | None = Field(
        default=None, description="Timestamp of last update."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of entity creation.",
    )

    @property
    def is_installed(self) -> bool:
        """Check if the package is currently installed."""
        return self.status in {
            PackageStatus.INSTALLED,
            PackageStatus.BROKEN,
            PackageStatus.UPDATING,
            PackageStatus.REPAIRING,
        }

    @property
    def has_update(self) -> bool:
        """Check if an update is available."""
        if self.installed_version is None or self.latest_version is None:
            return False
        return self.latest_version > self.installed_version

    @property
    def is_healthy(self) -> bool:
        """Check if the package is installed and healthy."""
        return self.status == PackageStatus.INSTALLED and self.health_score >= 80

    def mark_installed(self, version: Version, install_path: Path) -> None:
        """Transition to INSTALLED state after successful installation."""
        self.status = PackageStatus.INSTALLED
        self.installed_version = version
        self.install_path = install_path
        self.installed_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Transition to FAILED state after installation failure."""
        self.status = PackageStatus.FAILED

    def mark_broken(self) -> None:
        """Transition to BROKEN state after health check failure."""
        self.status = PackageStatus.BROKEN

    def mark_uninstalled(self) -> None:
        """Reset to AVAILABLE state after successful uninstallation."""
        self.status = PackageStatus.AVAILABLE
        self.installed_version = None
        self.install_path = None
        self.installed_at = None
        self.health_score = -1
        self.last_verified_at = None

    def update_health(self, score: int) -> None:
        """Update the health score after a health check."""
        self.health_score = max(0, min(100, score))
        self.last_verified_at = datetime.now(timezone.utc)
        if score < 40 and self.status == PackageStatus.INSTALLED:
            self.mark_broken()
