"""
Download cache manager implementation.

Caches downloaded installers with checksum validation to eliminate duplicate downloads.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

from src.config.settings import AppSettings
from src.core.value_objects.checksum import Checksum
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("downloader.cache")


class CacheManager:
    """
    Manages local installer cache in DEVFORGE_CACHE_DIR.
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        settings = AppSettings()
        self.cache_dir = cache_dir or settings.paths.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cached_file(self, file_name: str) -> Path | None:
        """
        Check if a file exists in the cache directory.
        """
        cached_path = self.cache_dir / file_name
        if cached_path.exists() and cached_path.is_file() and cached_path.stat().st_size > 0:
            return cached_path
        return None

    async def get_valid_cached_file(
        self,
        file_name: str,
        expected_checksum: Checksum | None,
    ) -> Path | None:
        """
        Check if a file exists in cache AND satisfies checksum verification.
        """
        cached_path = self.get_cached_file(file_name)
        if not cached_path:
            return None

        if expected_checksum:
            try:
                is_valid = await expected_checksum.verify_file(cached_path)
                if is_valid:
                    logger.info(f"Valid cached installer found for '{file_name}'.")
                    return cached_path
                else:
                    logger.warning(f"Cached file '{file_name}' checksum invalid. Deleting stale cache.")
                    cached_path.unlink(missing_ok=True)
                    return None
            except Exception:
                return None

        return cached_path

    async def put_in_cache(self, source_path: Path, file_name: str | None = None) -> Path:
        """
        Copy or move a downloaded file into the cache.
        """
        target_name = file_name or source_path.name
        target_path = self.cache_dir / target_name

        if source_path.resolve() != target_path.resolve():
            shutil.copy2(source_path, target_path)

        logger.info(f"Cached installer file as '{target_name}'.")
        return target_path

    def clear_cache() -> int:
        """Clear all cached installer files."""
        count = 0
        for item in self.cache_dir.glob("*"):
            if item.is_file():
                item.unlink(missing_ok=True)
                count += 1
        return count
