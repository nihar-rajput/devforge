"""
Download-related domain events.

Emitted by the download manager and consumed by the WebSocket handler
to stream real-time progress to the UI.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.core.enums import EventSeverity
from src.core.events.base import DomainEvent
from src.core.value_objects.package_id import PackageId


class DownloadStarted(DomainEvent):
    """Emitted when a download begins."""

    event_type: str = "DownloadStarted"
    package_id: PackageId = Field(..., description="Package being downloaded.")
    download_id: UUID = Field(..., description="Download task ID.")
    url: str = Field(..., description="Download URL.")
    file_name: str = Field(..., description="Target filename.")
    total_bytes: int | None = Field(default=None, description="Total size if known.")
    segment_count: int = Field(default=1, description="Number of download segments.")
    message: str = "Download started"


class DownloadProgressUpdated(DomainEvent):
    """Emitted periodically with download progress metrics."""

    event_type: str = "DownloadProgressUpdated"
    severity: EventSeverity = EventSeverity.DEBUG
    download_id: UUID = Field(..., description="Download task ID.")
    package_id: PackageId = Field(..., description="Package being downloaded.")
    downloaded_bytes: int = Field(..., description="Total bytes downloaded so far.")
    total_bytes: int | None = Field(default=None, description="Total size if known.")
    progress_percent: float = Field(..., description="Download progress 0-100.")
    speed_bytes_per_sec: float = Field(..., description="Current download speed.")
    eta_seconds: float | None = Field(default=None, description="Estimated time remaining.")
    message: str = "Download in progress"


class DownloadCompleted(DomainEvent):
    """Emitted when a download finishes successfully."""

    event_type: str = "DownloadCompleted"
    download_id: UUID = Field(..., description="Download task ID.")
    package_id: PackageId = Field(..., description="Package downloaded.")
    file_name: str = Field(..., description="Downloaded filename.")
    total_bytes: int = Field(..., description="Total bytes downloaded.")
    duration_seconds: float = Field(..., description="Total download time.")
    checksum_verified: bool = Field(..., description="Whether checksum was verified.")
    message: str = "Download completed"


class DownloadFailed(DomainEvent):
    """Emitted when a download fails after exhausting retries."""

    event_type: str = "DownloadFailed"
    severity: EventSeverity = EventSeverity.ERROR
    download_id: UUID = Field(..., description="Download task ID.")
    package_id: PackageId = Field(..., description="Package that failed to download.")
    error: str = Field(..., description="Error description.")
    retry_count: int = Field(..., description="Number of retries attempted.")
    message: str = "Download failed"


class DownloadPaused(DomainEvent):
    """Emitted when a download is paused."""

    event_type: str = "DownloadPaused"
    download_id: UUID = Field(..., description="Download task ID.")
    package_id: PackageId = Field(..., description="Package whose download was paused.")
    downloaded_bytes: int = Field(..., description="Bytes downloaded before pause.")
    message: str = "Download paused"


class DownloadResumed(DomainEvent):
    """Emitted when a paused download is resumed."""

    event_type: str = "DownloadResumed"
    download_id: UUID = Field(..., description="Download task ID.")
    package_id: PackageId = Field(..., description="Package whose download was resumed.")
    resume_from_byte: int = Field(..., description="Byte offset to resume from.")
    message: str = "Download resumed"


class DownloadCancelled(DomainEvent):
    """Emitted when a download is cancelled by the user."""

    event_type: str = "DownloadCancelled"
    severity: EventSeverity = EventSeverity.WARNING
    download_id: UUID = Field(..., description="Download task ID.")
    package_id: PackageId = Field(..., description="Package whose download was cancelled.")
    message: str = "Download cancelled"
