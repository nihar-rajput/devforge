"""
Unit tests for Download Manager components.
"""

from __future__ import annotations

from pathlib import Path
import pytest

from src.core.entities.download import Download
from src.core.enums import DownloadStatus
from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.downloader.cache_manager import CacheManager
from src.downloader.checksum_verifier import ChecksumVerifier
from src.downloader.progress_tracker import ProgressTracker
from src.downloader.retry_policy import ExponentialBackoffRetry


def test_progress_tracker() -> None:
    tracker = ProgressTracker(total_bytes=1000)
    pct, eta, spd = tracker.update(500)
    assert pct == 50.0


def test_retry_policy_delay() -> None:
    retry = ExponentialBackoffRetry(max_retries=3, base_delay=1.0)
    delay0 = retry.compute_delay(0)
    assert 1.0 <= delay0 <= 1.2


@pytest.mark.asyncio
async def test_checksum_verifier_success(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello devforge")

    import hashlib
    h = hashlib.sha256(b"hello devforge").hexdigest()
    cs = Checksum.sha256(h)

    verifier = ChecksumVerifier()
    result = await verifier.verify(test_file, cs)
    assert result is True


@pytest.mark.asyncio
async def test_cache_manager(tmp_path: Path) -> None:
    cache = CacheManager(cache_dir=tmp_path / "cache")
    dummy_file = tmp_path / "installer.exe"
    dummy_file.write_bytes(b"installer binary content")

    cached_path = await cache.put_in_cache(dummy_file, "installer.exe")
    assert cached_path.exists()
    assert cache.get_cached_file("installer.exe") is not None
