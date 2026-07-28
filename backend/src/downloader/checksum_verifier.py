"""
Checksum verifier module.
"""

from __future__ import annotations

from pathlib import Path

from src.core.errors.download_errors import ChecksumMismatchError
from src.core.value_objects.checksum import Checksum
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("downloader.checksum")


class ChecksumVerifier:
    """
    Verifies cryptographic hash checksums of downloaded files.
    """

    async def verify(self, file_path: Path, expected_checksum: Checksum | None) -> bool:
        """
        Verify file checksum against expected checksum value.

        Args:
            file_path: Path to downloaded file.
            expected_checksum: Checksum value object, or None to skip.

        Returns:
            True if verification passed or skipped.

        Raises:
            ChecksumMismatchError: If checksum verification fails.
        """
        if expected_checksum is None:
            logger.debug(f"Checksum verification skipped for '{file_path.name}' (no checksum provided).")
            return True

        if not file_path.exists():
            raise FileNotFoundError(f"Cannot verify checksum: file '{file_path}' does not exist.")

        logger.info(f"Verifying {expected_checksum.algorithm.value.upper()} checksum for '{file_path.name}'...")
        is_valid = await expected_checksum.verify_file(file_path)

        if not is_valid:
            actual = await Checksum.compute_for_file(file_path, expected_checksum.algorithm)
            logger.error(
                f"Checksum mismatch for '{file_path.name}'. Expected: {expected_checksum.value}, Got: {actual.value}"
            )
            raise ChecksumMismatchError(
                url=str(file_path),
                expected=expected_checksum.value,
                actual=actual.value,
            )

        logger.info(f"Checksum verification passed for '{file_path.name}'.")
        return True
