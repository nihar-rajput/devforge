"""
Download entity.

Represents a download task with support for multi-segment parallel
downloading, pause/resume, and progress tracking.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core.enums import DownloadStatus
from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId


class DownloadSegment(BaseModel):
    """
    A segment of a multi-segment download.

    Large files are split into segments that download in parallel
    to maximize bandwidth utilization. Each segment tracks its own
    byte range and progress for pause/resume support.
    """

    index: int = Field(..., ge=0, description="Segment index (0-based).")
    start_byte: int = Field(..., ge=0, description="First byte of this segment's range.")
    end_byte: int = Field(..., ge=0, description="Last byte of this segment's range (inclusive).")
    downloaded_bytes: int = Field(
        default=0, ge=0, description="Bytes downloaded so far in this segment."
    )
    status: DownloadStatus = Field(
        default=DownloadStatus.PENDING,
        description="Current status of this segment.",
    )

    @property
    def total_bytes(self) -> int:
        """Total bytes this segment needs to download."""
        return self.end_byte - self.start_byte + 1

    @property
    def progress_percent(self) -> float:
        """Download progress as a percentage."""
        if self.total_bytes == 0:
            return 100.0
        return min(100.0, (self.downloaded_bytes / self.total_bytes) * 100)

    @property
    def is_complete(self) -> bool:
        """Check if this segment has finished downloading."""
        return self.downloaded_bytes >= self.total_bytes

    @property
    def remaining_bytes(self) -> int:
        """Bytes still to download."""
        return max(0, self.total_bytes - self.downloaded_bytes)


class Download(BaseModel):
    """
    A download task for a package installer or artifact.

    Supports multi-segment parallel downloading for large files,
    with pause/resume via byte offset persistence. Progress is
    streamed to the UI via WebSocket events.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique download task ID.")
    package_id: PackageId = Field(..., description="Package this download is for.")
    url: str = Field(..., description="Download URL.")
    file_name: str = Field(..., description="Target filename.")
    total_size: FileSize | None = Field(
        default=None, description="Total file size (None if unknown)."
    )
    expected_checksum: Checksum | None = Field(
        default=None, description="Expected checksum for verification."
    )
    status: DownloadStatus = Field(
        default=DownloadStatus.PENDING,
        description="Current download status.",
    )
    segments: list[DownloadSegment] = Field(
        default_factory=list,
        description="Download segments for parallel downloading.",
    )
    downloaded_bytes: int = Field(
        default=0, ge=0, description="Total bytes downloaded across all segments."
    )
    speed_bytes_per_sec: float = Field(
        default=0.0, ge=0.0, description="Current download speed."
    )
    eta_seconds: float | None = Field(
        default=None, description="Estimated time to completion in seconds."
    )
    retry_count: int = Field(
        default=0, ge=0, description="Number of retry attempts so far."
    )
    max_retries: int = Field(
        default=3, ge=0, description="Maximum retry attempts."
    )
    started_at: datetime | None = Field(
        default=None, description="When the download started."
    )
    completed_at: datetime | None = Field(
        default=None, description="When the download completed."
    )
    error_message: str | None = Field(
        default=None, description="Error details if download failed."
    )

    @property
    def progress_percent(self) -> float:
        """Overall download progress as a percentage."""
        if self.total_size is None or self.total_size.bytes_count == 0:
            return 0.0
        return min(100.0, (self.downloaded_bytes / self.total_size.bytes_count) * 100)

    @property
    def is_segmented(self) -> bool:
        """Check if this is a multi-segment download."""
        return len(self.segments) > 1

    @property
    def can_retry(self) -> bool:
        """Check if there are retries remaining."""
        return self.retry_count < self.max_retries

    @property
    def speed_human(self) -> str:
        """Human-readable download speed."""
        return str(FileSize(bytes_count=int(self.speed_bytes_per_sec))) + "/s"

    def start(self) -> None:
        """Mark the download as started."""
        self.status = DownloadStatus.IN_PROGRESS
        self.started_at = datetime.now(timezone.utc)

    def pause(self) -> None:
        """Pause the download."""
        self.status = DownloadStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused download."""
        self.status = DownloadStatus.IN_PROGRESS

    def complete(self) -> None:
        """Mark the download as completed."""
        self.status = DownloadStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        if self.total_size:
            self.downloaded_bytes = self.total_size.bytes_count

    def fail(self, error: str) -> None:
        """Mark the download as failed."""
        self.status = DownloadStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        """Cancel the download."""
        self.status = DownloadStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)

    def increment_retry(self) -> None:
        """Increment the retry counter."""
        self.retry_count += 1

    def update_progress(
        self,
        downloaded_bytes: int,
        speed_bytes_per_sec: float,
    ) -> None:
        """Update download progress metrics."""
        self.downloaded_bytes = downloaded_bytes
        self.speed_bytes_per_sec = speed_bytes_per_sec
        if self.total_size and speed_bytes_per_sec > 0:
            remaining = self.total_size.bytes_count - downloaded_bytes
            self.eta_seconds = remaining / speed_bytes_per_sec
