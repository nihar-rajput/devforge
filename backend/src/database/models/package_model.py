"""
SQLAlchemy ORM model for Package entity and dependencies.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.entities.package import Dependency, Package, PluginMetadata
from src.core.enums import Category, PackageStatus, UpdateStrategy
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.system_requirements import SystemRequirements
from src.core.value_objects.version import Version
from src.database.session import Base

if TYPE_CHECKING:
    pass


class PackageModel(Base):
    """
    SQLAlchemy ORM model for packages table.
    """

    __tablename__ = "packages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    documentation_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default=PackageStatus.AVAILABLE.value, index=True)
    installed_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latest_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    install_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    update_strategy: Mapped[str] = mapped_column(String(30), nullable=False, default=UpdateStrategy.IN_PLACE.value)
    health_score: Mapped[int] = mapped_column(Integer, nullable=False, default=-1)

    system_requirements_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    dependencies_rel: Mapped[list[DependencyModel]] = relationship(
        "DependencyModel",
        back_populates="package_rel",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_domain(self) -> Package:
        """Convert ORM model to domain entity."""
        metadata = PluginMetadata(
            id=PackageId.of(self.id),
            name=self.name,
            description=self.description,
            category=Category(self.category),
            icon=self.icon,
            website=self.website,
            documentation_url=self.documentation_url,
        )

        dependencies = [dep.to_domain() for dep in self.dependencies_rel]
        sys_reqs = SystemRequirements.model_validate_json(self.system_requirements_json or "{}")

        return Package(
            id=PackageId.of(self.id),
            metadata=metadata,
            status=PackageStatus(self.status),
            installed_version=Version.parse(self.installed_version) if self.installed_version else None,
            latest_version=Version.parse(self.latest_version) if self.latest_version else None,
            install_path=Path(self.install_path) if self.install_path else None,
            dependencies=dependencies,
            system_requirements=sys_reqs,
            update_strategy=UpdateStrategy(self.update_strategy),
            health_score=self.health_score,
            installed_at=self.installed_at,
            last_verified_at=self.last_verified_at,
            last_updated_at=self.last_updated_at,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, domain: Package) -> PackageModel:
        """Convert domain entity to ORM model."""
        model = cls(
            id=domain.id.value,
            name=domain.metadata.name,
            description=domain.metadata.description,
            category=domain.metadata.category.value,
            icon=domain.metadata.icon,
            website=domain.metadata.website,
            documentation_url=domain.metadata.documentation_url,
            status=domain.status.value,
            installed_version=str(domain.installed_version) if domain.installed_version else None,
            latest_version=str(domain.latest_version) if domain.latest_version else None,
            install_path=str(domain.install_path) if domain.install_path else None,
            update_strategy=domain.update_strategy.value,
            health_score=domain.health_score,
            system_requirements_json=domain.system_requirements.model_dump_json(),
            installed_at=domain.installed_at,
            last_verified_at=domain.last_verified_at,
            last_updated_at=domain.last_updated_at,
            created_at=domain.created_at,
        )
        model.dependencies_rel = [
            DependencyModel.from_domain(domain.id.value, dep) for dep in domain.dependencies
        ]
        return model


class DependencyModel(Base):
    """
    SQLAlchemy ORM model for package dependencies.
    """

    __tablename__ = "package_dependencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_id: Mapped[str] = mapped_column(String(64), ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    dependency_package_id: Mapped[str] = mapped_column(String(64), nullable=False)
    version_constraint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    optional: Mapped[bool] = mapped_column(nullable=False, default=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    package_rel: Mapped[PackageModel] = relationship("PackageModel", back_populates="dependencies_rel")

    def to_domain(self) -> Dependency:
        """Convert ORM model to domain value object."""
        return Dependency(
            package_id=PackageId.of(self.dependency_package_id),
            version_constraint=self.version_constraint,
            optional=self.optional,
            reason=self.reason,
        )

    @classmethod
    def from_domain(cls, package_id: str, domain: Dependency) -> DependencyModel:
        """Convert domain value object to ORM model."""
        return cls(
            package_id=package_id,
            dependency_package_id=domain.package_id.value,
            version_constraint=domain.version_constraint,
            optional=domain.optional,
            reason=domain.reason,
        )
