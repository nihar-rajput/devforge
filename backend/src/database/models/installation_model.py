"""
SQLAlchemy ORM model for Installation entity and InstallationStep.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.entities.installation import Installation, InstallationStep
from src.core.enums import InstallationStage
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.database.session import Base


class InstallationModel(Base):
    """SQLAlchemy ORM model for installations table."""

    __tablename__ = "installations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    package_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_version: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default=InstallationStage.QUEUED.value)
    progress_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    steps_rel: Mapped[list[InstallationStepModel]] = relationship(
        "InstallationStepModel",
        back_populates="installation_rel",
        cascade="all, delete-orphan",
        order_by="InstallationStepModel.step_index",
        lazy="selectin",
    )

    def to_domain(self) -> Installation:
        """Convert ORM model to domain Installation entity."""
        steps = [step.to_domain() for step in self.steps_rel]
        return Installation(
            id=UUID(self.id),
            package_id=PackageId.of(self.package_id),
            target_version=Version.parse(self.target_version),
            previous_version=Version.parse(self.previous_version) if self.previous_version else None,
            current_stage=InstallationStage(self.current_stage),
            steps=steps,
            progress_percent=self.progress_percent,
            started_at=self.started_at,
            completed_at=self.completed_at,
            is_cancelled=self.is_cancelled,
            error_summary=self.error_summary,
        )

    @classmethod
    def from_domain(cls, domain: Installation) -> InstallationModel:
        """Convert domain entity to ORM model."""
        model = cls(
            id=str(domain.id),
            package_id=domain.package_id.value,
            target_version=str(domain.target_version),
            previous_version=str(domain.previous_version) if domain.previous_version else None,
            current_stage=domain.current_stage.value,
            progress_percent=domain.progress_percent,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            is_cancelled=domain.is_cancelled,
            error_summary=domain.error_summary,
        )
        model.steps_rel = [
            InstallationStepModel.from_domain(str(domain.id), idx, step)
            for idx, step in enumerate(domain.steps)
        ]
        return model


class InstallationStepModel(Base):
    """SQLAlchemy ORM model for installation steps table."""

    __tablename__ = "installation_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    installation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("installations.id", ondelete="CASCADE"), nullable=False
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    rollback_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    rollback_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    installation_rel: Mapped[InstallationModel] = relationship("InstallationModel", back_populates="steps_rel")

    def to_domain(self) -> InstallationStep:
        """Convert ORM model to domain InstallationStep value object/entity."""
        rollback_data = json.loads(self.rollback_data_json) if self.rollback_data_json else None
        return InstallationStep(
            stage=InstallationStage(self.stage),
            message=self.message,
            started_at=self.started_at,
            completed_at=self.completed_at,
            success=self.success,
            error_message=self.error_message,
            rollback_command=self.rollback_command,
            rollback_data=rollback_data,
        )

    @classmethod
    def from_domain(cls, installation_id: str, step_index: int, domain: InstallationStep) -> InstallationStepModel:
        """Convert domain value object/entity to ORM model."""
        rollback_json = json.dumps(domain.rollback_data) if domain.rollback_data else None
        return cls(
            installation_id=installation_id,
            step_index=step_index,
            stage=domain.stage.value,
            message=domain.message,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            success=domain.success,
            error_message=domain.error_message,
            rollback_command=domain.rollback_command,
            rollback_data_json=rollback_json,
        )
