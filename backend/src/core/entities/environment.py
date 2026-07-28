"""
Environment profile and stack definition entities.

Supports saving and restoring complete development environment
configurations (snapshot & restore feature).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version


class PackageSnapshot(BaseModel):
    """
    A frozen reference to a specific package version within a profile.

    This is the data format used when exporting/importing profiles.
    """

    package_id: PackageId = Field(..., description="Package identifier.")
    version: Version = Field(..., description="Exact version to install.")
    pinned: bool = Field(
        default=False,
        description="If True, updates are blocked for this package in the profile.",
    )


class StackDefinition(BaseModel):
    """
    A predefined development stack.

    Stacks are the high-level selections shown on the welcome screen
    (e.g., 'Python Development', 'AI / Machine Learning'). Each stack
    expands into a concrete list of packages.

    Stack definitions are built into DevForge and not user-modifiable
    (users customize packages after selecting a stack).
    """

    id: str = Field(..., description="Stack identifier (e.g., 'python-dev', 'ai-ml').")
    name: str = Field(..., description="Display name (e.g., 'Python Development').")
    description: str = Field(..., description="Brief description of the stack.")
    icon: str | None = Field(default=None, description="Icon filename.")
    packages: list[PackageId] = Field(
        ..., min_length=1, description="Default packages for this stack."
    )
    optional_packages: list[PackageId] = Field(
        default_factory=list,
        description="Optional packages the user can add during customization.",
    )
    conditional_packages: dict[str, list[PackageId]] = Field(
        default_factory=dict,
        description=(
            "Packages added based on system conditions. "
            "Key is condition name (e.g., 'nvidia_gpu'), value is packages to add."
        ),
    )


class EnvironmentProfile(BaseModel):
    """
    A user-created environment profile.

    Profiles capture the complete state of a development environment
    so it can be exported as JSON and imported on another machine.

    This is the 'snapshot & restore' feature — like package-lock.json
    for your entire dev setup.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique profile ID.")
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User-given name (e.g., 'AI Workstation').",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description.",
    )
    packages: list[PackageSnapshot] = Field(
        default_factory=list,
        description="Packages and their versions in this profile.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the profile was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the profile was last modified.",
    )
    source_stack_id: str | None = Field(
        default=None,
        description="Stack ID this profile was originally created from, if any.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="User-defined tags for organization.",
    )

    @property
    def package_count(self) -> int:
        """Number of packages in this profile."""
        return len(self.packages)

    def add_package(self, package_id: PackageId, version: Version) -> None:
        """Add a package to this profile."""
        existing_ids = {snap.package_id for snap in self.packages}
        if package_id not in existing_ids:
            self.packages.append(PackageSnapshot(package_id=package_id, version=version))
            self.updated_at = datetime.now(timezone.utc)

    def remove_package(self, package_id: PackageId) -> None:
        """Remove a package from this profile."""
        self.packages = [snap for snap in self.packages if snap.package_id != package_id]
        self.updated_at = datetime.now(timezone.utc)

    def get_package_ids(self) -> list[PackageId]:
        """Get all package IDs in this profile."""
        return [snap.package_id for snap in self.packages]
