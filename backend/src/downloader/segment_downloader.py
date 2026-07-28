"""
Multi-segment parallel HTTP downloader implementation.

Uses aiohttp and HTTP Range headers to download large files in parallel chunks.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable, List

import aiofiles
import aiohttp

from src.core.entities.download import DownloadSegment
from src.core.enums import DownloadStatus
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("downloader.segment")


class SegmentDownloader:
    """
    Downloads HTTP files using multi-segment parallel byte-range requests.
    """

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def download_segments(
        self,
        url: str,
        destination: Path,
        segments: List[DownloadSegment],
        on_progress: Callable[[int], None] | None = None,
    ) -> None:
        """
        Download file segments in parallel.

        Args:
            url: Download URL.
            destination: Path to write destination file.
            segments: List of DownloadSegment objects representing byte ranges.
            on_progress: Callback for overall bytes written update.
        """
        # Ensure destination file exists and has total allocation
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            async with aiofiles.open(destination, "wb") as f:
                pass

        tasks = [
            self._download_single_segment(url, destination, seg, on_progress)
            for seg in segments
        ]

        await asyncio.gather(*tasks)

    async def _download_single_segment(
        self,
        url: str,
        destination: Path,
        segment: DownloadSegment,
        on_progress: Callable[[int], None] | None = None,
    ) -> None:
        """Download one segment byte range and write into file at correct byte offset."""
        current_offset = segment.start_byte + segment.downloaded_bytes
        if current_offset > segment.end_byte:
            segment.status = DownloadStatus.COMPLETED
            return

        headers = {"Range": f"bytes={current_offset}-{segment.end_byte}"}
        segment.status = DownloadStatus.IN_PROGRESS

        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status not in (200, 206):
                    raise ValueError(f"HTTP error {resp.status} for segment {segment.index}")

                async with aiofiles.open(destination, "r+b") as f:
                    await f.seek(current_offset)
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:
                            break

                        await f.write(chunk)
                        chunk_size = len(chunk)
                        segment.downloaded_bytes += chunk_size
                        if on_progress:
                            on_progress(chunk_size)

            segment.status = DownloadStatus.COMPLETED

        except Exception as exc:
            segment.status = DownloadStatus.FAILED
            logger.error(f"Segment {segment.index} failed: {exc}")
            raise
