"""
SQLAlchemy ORM model for Download entity and DownloadSegment.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.entities.download import Download, DownloadSegment
from src.core.enums import DownloadStatus
from src.core.value_objects.checksum import Checksum, HashAlgorithm
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.database.session import Base


class DownloadModel(Base):
    """SQLAlchemy ORM model for downloads table."""

    __tablename__ = "downloads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    package_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_checksum_algorithm: Mapped[str | None] = mapped_column(String(20), nullable=True)
    expected_checksum_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=DownloadStatus.PENDING.value, index=True)
    downloaded_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    speed_bytes_per_sec: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    eta_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    segments_rel: Mapped[list[DownloadSegmentModel]] = relationship(
        "DownloadSegmentModel",
        back_populates="download_rel",
        cascade="all, delete-orphan",
        order_by="DownloadSegmentModel.segment_index",
        lazy="selectin",
    )

    def to_domain(self) -> Download:
        """Convert ORM model to domain Download entity."""
        checksum = None
        if self.expected_checksum_algorithm and self.expected_checksum_value:
            checksum = Checksum(
                algorithm=HashAlgorithm(self.expected_checksum_algorithm),
                value=self.expected_checksum_value,
            )

        segments = [seg.to_domain() for seg in self.segments_rel]

        return Download(
            id=UUID(self.id),
            package_id=PackageId.of(self.package_id),
            url=self.url,
            file_name=self.file_name,
            total_size=FileSize(bytes_count=self.total_size_bytes) if self.total_size_bytes is not None else None,
            expected_checksum=checksum,
            status=DownloadStatus(self.status),
            segments=segments,
            downloaded_bytes=self.downloaded_bytes,
            speed_bytes_per_sec=self.speed_bytes_per_sec,
            eta_seconds=self.eta_seconds,
            retry_count=self.retry_count,
            max_retries=self.max_retries,
            started_at=self.started_at,
            completed_at=self.completed_at,
            error_message=self.error_message,
        )

    @classmethod
    def from_domain(cls, domain: Download) -> DownloadModel:
        """Convert domain entity to ORM model."""
        checksum_algo = domain.expected_checksum.algorithm.value if domain.expected_checksum else None
        checksum_val = domain.expected_checksum.value if domain.expected_checksum else None

        model = cls(
            id=str(domain.id),
            package_id=domain.package_id.value,
            url=domain.url,
            file_name=domain.file_name,
            total_size_bytes=domain.total_size.bytes_count if domain.total_size else None,
            expected_checksum_algorithm=checksum_algo,
            expected_checksum_value=checksum_val,
            status=domain.status.value,
            downloaded_bytes=domain.downloaded_bytes,
            speed_bytes_per_sec=domain.speed_bytes_per_sec,
            eta_seconds=domain.eta_seconds,
            retry_count=domain.retry_count,
            max_retries=domain.max_retries,
            started_at=domain.started_at,
            completed_at=domain.completed_at,
            error_message=domain.error_message,
        )
        model.segments_rel = [
            DownloadSegmentModel.from_domain(str(domain.id), seg) for seg in domain.segments
        ]
        return model


class DownloadSegmentModel(Base):
    """SQLAlchemy ORM model for download segments table."""

    __tablename__ = "download_segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    download_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("downloads.id", ondelete="CASCADE"), nullable=False
    )
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_byte: Mapped[int] = mapped_column(Integer, nullable=False)
    end_byte: Mapped[int] = mapped_column(Integer, nullable=False)
    downloaded_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=DownloadStatus.PENDING.value)

    download_rel: Mapped[DownloadModel] = relationship("DownloadModel", back_populates="segments_rel")

    def to_domain(self) -> DownloadSegment:
        """Convert ORM model to domain DownloadSegment."""
        return DownloadSegment(
            index=self.segment_index,
            start_byte=self.start_byte,
            end_byte=self.end_byte,
            downloaded_bytes=self.downloaded_bytes,
            status=DownloadStatus(self.status),
        )

    @classmethod
    def from_domain(cls, download_id: str, domain: DownloadSegment) -> DownloadSegmentModel:
        """Convert domain DownloadSegment to ORM model."""
        return cls(
            download_id=download_id,
            segment_index=domain.index,
            start_byte=domain.start_byte,
            end_byte=domain.end_byte,
            downloaded_bytes=domain.downloaded_bytes,
            status=domain.status.value,
        )
