"""
SQLAlchemy ORM model for EnvironmentProfile entity and PackageSnapshot.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.entities.environment import EnvironmentProfile, PackageSnapshot
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.database.session import Base


class EnvironmentProfileModel(Base):
    """SQLAlchemy ORM model for environment profiles table."""

    __tablename__ = "environment_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_stack_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    packages_rel: Mapped[list[PackageSnapshotModel]] = relationship(
        "PackageSnapshotModel",
        back_populates="profile_rel",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_domain(self) -> EnvironmentProfile:
        """Convert ORM model to domain EnvironmentProfile."""
        tags = json.loads(self.tags_json) if self.tags_json else []
        packages = [snap.to_domain() for snap in self.packages_rel]

        return EnvironmentProfile(
            id=UUID(self.id),
            name=self.name,
            description=self.description,
            packages=packages,
            created_at=self.created_at,
            updated_at=self.updated_at,
            source_stack_id=self.source_stack_id,
            tags=tags,
        )

    @classmethod
    def from_domain(cls, domain: EnvironmentProfile) -> EnvironmentProfileModel:
        """Convert domain entity to ORM model."""
        tags_json = json.dumps(domain.tags)
        model = cls(
            id=str(domain.id),
            name=domain.name,
            description=domain.description,
            source_stack_id=domain.source_stack_id,
            tags_json=tags_json,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )
        model.packages_rel = [
            PackageSnapshotModel.from_domain(str(domain.id), snap) for snap in domain.packages
        ]
        return model


class PackageSnapshotModel(Base):
    """SQLAlchemy ORM model for profile package snapshots table."""

    __tablename__ = "profile_package_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("environment_profiles.id", ondelete="CASCADE"), nullable=False
    )
    package_id: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    profile_rel: Mapped[EnvironmentProfileModel] = relationship(
        "EnvironmentProfileModel", back_populates="packages_rel"
    )

    def to_domain(self) -> PackageSnapshot:
        """Convert ORM model to domain PackageSnapshot."""
        return PackageSnapshot(
            package_id=PackageId.of(self.package_id),
            version=Version.parse(self.version),
            pinned=self.pinned,
        )

    @classmethod
    def from_domain(cls, profile_id: str, domain: PackageSnapshot) -> PackageSnapshotModel:
        """Convert domain PackageSnapshot to ORM model."""
        return cls(
            profile_id=profile_id,
            package_id=domain.package_id.value,
            version=str(domain.version),
            pinned=domain.pinned,
        )
