"""
Download backend port.

Abstract interface for performing HTTP downloads with support
for segmented parallel downloading, pause/resume, and progress.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncIterator

from src.core.entities.download import Download


class DownloadBackend(ABC):
    """
    Abstract interface for the download engine.

    Implementations handle the actual HTTP transfer, including
    segmented parallel downloads, Range header support, and
    connection management.
    """

    @abstractmethod
    async def start_download(self, download: Download, destination: Path) -> None:
        """
        Start downloading a file.

        For files above the segment threshold, this should use
        multi-segment parallel downloading. The download entity's
        progress fields should be updated in real-time.

        Args:
            download: Download entity with URL and metadata.
            destination: Local path to save the file.
        """

    @abstractmethod
    async def pause_download(self, download: Download) -> None:
        """
        Pause an active download.

        Must persist segment byte offsets for resume capability.

        Args:
            download: Download entity to pause.
        """

    @abstractmethod
    async def resume_download(self, download: Download, destination: Path) -> None:
        """
        Resume a paused download from the last checkpoint.

        Args:
            download: Download entity to resume (contains byte offsets).
            destination: Local path to save/append the file.
        """

    @abstractmethod
    async def cancel_download(self, download: Download) -> None:
        """
        Cancel a download and clean up partial files.

        Args:
            download: Download entity to cancel.
        """

    @abstractmethod
    async def get_file_size(self, url: str) -> int | None:
        """
        Query the server for the file size without downloading.

        Args:
            url: URL to query.

        Returns:
            File size in bytes, or None if the server doesn't report it.
        """

    @abstractmethod
    async def supports_range_requests(self, url: str) -> bool:
        """
        Check if the server supports HTTP Range requests (for resume/segments).

        Args:
            url: URL to check.

        Returns:
            True if the server supports Range requests.
        """

    @abstractmethod
    def stream_progress(self, download: Download) -> AsyncIterator[float]:
        """
        Yield progress updates as an async iterator.

        Args:
            download: Download entity to monitor.

        Yields:
            Progress percentage (0.0 - 100.0).
        """
