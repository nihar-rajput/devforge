"""
Default DownloadManager orchestrator implementation.

Implements DownloadBackend port with cache checking, segmented parallel downloading,
pause/resume offset persistence, progress streaming, checksum verification,
and domain event publishing.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator, Dict

import aiohttp

from src.config.settings import AppSettings
from src.core.entities.download import Download, DownloadSegment
from src.core.enums import DownloadStatus
from src.core.events.download_events import (
    DownloadCancelled,
    DownloadCompleted,
    DownloadFailed,
    DownloadPaused,
    DownloadProgressUpdated,
    DownloadResumed,
    DownloadStarted,
)
from src.core.ports.download_backend import DownloadBackend
from src.core.ports.event_bus import EventBus
from src.downloader.cache_manager import CacheManager
from src.downloader.checksum_verifier import ChecksumVerifier
from src.downloader.progress_tracker import ProgressTracker
from src.downloader.retry_policy import ExponentialBackoffRetry
from src.downloader.segment_downloader import SegmentDownloader
from src.logger.structured_logger import StructuredLogger
from src.utils.async_helpers import ConcurrencyLimiter

logger = StructuredLogger("downloader.manager")


class DefaultDownloadManager(DownloadBackend):
    """
    Concrete implementation of DownloadBackend port interface.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        cache_manager: CacheManager | None = None,
        checksum_verifier: ChecksumVerifier | None = None,
    ) -> None:
        settings = AppSettings()
        self._event_bus = event_bus
        self._cache_manager = cache_manager or CacheManager()
        self._checksum_verifier = checksum_verifier or ChecksumVerifier()
        self._limiter = ConcurrencyLimiter(settings.download.max_concurrent_downloads)
        self._segment_threshold = settings.download.segment_threshold_mb * 1024 * 1024
        self._segment_count = settings.download.segment_count
        self._active_downloads: Dict[str, Download] = {}
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300)
            )
        return self._session

    async def get_file_size(self, url: str) -> int | None:
        session = await self._get_session()
        try:
            async with session.head(url, allow_redirects=True) as resp:
                if resp.status == 200:
                    content_len = resp.headers.get("Content-Length")
                    if content_len and content_len.isdigit():
                        return int(content_len)
        except Exception as exc:
            logger.debug(f"Failed HEAD request to '{url}': {exc}")
        return None

    async def supports_range_requests(self, url: str) -> bool:
        session = await self._get_session()
        try:
            async with session.head(url, headers={"Range": "bytes=0-0"}, allow_redirects=True) as resp:
                return resp.status in (200, 206) and resp.headers.get("Accept-Ranges") == "bytes"
        except Exception:
            return False

    async def start_download(self, download: Download, destination: Path) -> None:
        # Check cache first
        cached = await self._cache_manager.get_valid_cached_file(
            download.file_name, download.expected_checksum
        )
        if cached:
            download.status = DownloadStatus.CACHED
            download.completed_at = download.started_at
            if self._event_bus:
                await self._event_bus.publish(
                    DownloadCompleted(
                        download_id=download.id,
                        package_id=download.package_id,
                        file_name=download.file_name,
                        total_bytes=cached.stat().st_size,
                        duration_seconds=0.0,
                        checksum_verified=True,
                    )
                )
            return

        async with self._limiter:
            self._active_downloads[str(download.id)] = download
            download.start()

            if self._event_bus:
                await self._event_bus.publish(
                    DownloadStarted(
                        download_id=download.id,
                        package_id=download.package_id,
                        url=download.url,
                        file_name=download.file_name,
                        total_bytes=download.total_size.bytes_count if download.total_size else None,
                        segment_count=self._segment_count if download.is_segmented else 1,
                    )
                )

            try:
                # Query file size if not known
                if not download.total_size:
                    size = await self.get_file_size(download.url)
                    if size:
                        from src.core.value_objects.file_size import FileSize
                        download.total_size = FileSize(bytes_count=size)

                session = await self._get_session()
                tracker = ProgressTracker(download.total_size.bytes_count if download.total_size else None)

                # Determine if segmented download is suitable
                if (
                    download.total_size
                    and download.total_size.bytes_count >= self._segment_threshold
                    and await self.supports_range_requests(download.url)
                ):
                    # Setup segments
                    total = download.total_size.bytes_count
                    seg_size = total // self._segment_count
                    segments: list[DownloadSegment] = []
                    for i in range(self._segment_count):
                        start = i * seg_size
                        end = (start + seg_size - 1) if i < self._segment_count - 1 else total - 1
                        segments.append(DownloadSegment(index=i, start_byte=start, end_byte=end))
                    download.segments = segments

                    seg_downloader = SegmentDownloader(session)

                    def on_bytes(written: int) -> None:
                        download.downloaded_bytes += written
                        pct, eta, spd = tracker.update(download.downloaded_bytes)
                        download.speed_bytes_per_sec = spd
                        download.eta_seconds = eta

                    await seg_downloader.download_segments(
                        download.url, destination, download.segments, on_bytes
                    )
                else:
                    # Single stream download
                    async with session.get(download.url) as resp:
                        if resp.status != 200:
                            raise ValueError(f"HTTP GET failed with status {resp.status}")

                        import aiofiles
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        async with aiofiles.open(destination, "wb") as f:
                            while True:
                                chunk = await resp.content.read(8192)
                                if not chunk:
                                    break
                                await f.write(chunk)
                                download.downloaded_bytes += len(chunk)
                                pct, eta, spd = tracker.update(download.downloaded_bytes)
                                download.speed_bytes_per_sec = spd
                                download.eta_seconds = eta

                # Verify checksum
                await self._checksum_verifier.verify(destination, download.expected_checksum)

                # Put in cache
                await self._cache_manager.put_in_cache(destination, download.file_name)

                download.complete()
                logger.info(f"Download completed for '{download.file_name}'.")

                if self._event_bus:
                    await self._event_bus.publish(
                        DownloadCompleted(
                            download_id=download.id,
                            package_id=download.package_id,
                            file_name=download.file_name,
                            total_bytes=download.downloaded_bytes,
                            duration_seconds=tracker.last_time - tracker.start_time,
                            checksum_verified=download.expected_checksum is not None,
                        )
                    )

            except Exception as exc:
                download.fail(str(exc))
                logger.error(f"Download failed for '{download.file_name}': {exc}")
                if self._event_bus:
                    await self._event_bus.publish(
                        DownloadFailed(
                            download_id=download.id,
                            package_id=download.package_id,
                            error=str(exc),
                            retry_count=download.retry_count,
                        )
                    )
                raise
            finally:
                self._active_downloads.pop(str(download.id), None)

    async def pause_download(self, download: Download) -> None:
        download.pause()
        if self._event_bus:
            await self._event_bus.publish(
                DownloadPaused(
                    download_id=download.id,
                    package_id=download.package_id,
                    downloaded_bytes=download.downloaded_bytes,
                )
            )

    async def resume_download(self, download: Download, destination: Path) -> None:
        download.resume()
        if self._event_bus:
            await self._event_bus.publish(
                DownloadResumed(
                    download_id=download.id,
                    package_id=download.package_id,
                    resume_from_byte=download.downloaded_bytes,
                )
            )
        await self.start_download(download, destination)

    async def cancel_download(self, download: Download) -> None:
        download.cancel()
        if self._event_bus:
            await self._event_bus.publish(
                DownloadCancelled(
                    download_id=download.id,
                    package_id=download.package_id,
                )
            )

    async def stream_progress(self, download: Download) -> AsyncIterator[float]:
        while download.status == DownloadStatus.IN_PROGRESS:
            yield download.progress_percent
            await asyncio.sleep(0.5)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
