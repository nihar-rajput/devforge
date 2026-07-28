"""
Checksum value object.

Represents a cryptographic hash for download integrity verification.
Supports SHA-256 (preferred) and MD5 (legacy fallback).
"""

from __future__ import annotations

import hashlib
from enum import StrEnum, unique
from pathlib import Path

from pydantic import BaseModel, Field


@unique
class HashAlgorithm(StrEnum):
    """Supported hash algorithms for checksum verification."""

    SHA256 = "sha256"
    MD5 = "md5"


class Checksum(BaseModel):
    """
    Cryptographic checksum for verifying file integrity.

    DevForge requires checksum verification for every downloaded installer
    to prevent corrupted or tampered files from being executed.

    Usage:
        checksum = Checksum(algorithm=HashAlgorithm.SHA256, value="abc123...")
        is_valid = await checksum.verify_file(Path("installer.exe"))
    """

    model_config = {"frozen": True}

    algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.SHA256,
        description="Hash algorithm used to compute the checksum.",
    )
    value: str = Field(
        ...,
        min_length=32,
        max_length=128,
        pattern=r"^[a-fA-F0-9]+$",
        description="Hexadecimal hash digest string.",
    )

    def __str__(self) -> str:
        return f"{self.algorithm}:{self.value}"

    def __hash__(self) -> int:
        return hash((self.algorithm, self.value.lower()))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Checksum):
            return (
                self.algorithm == other.algorithm
                and self.value.lower() == other.value.lower()
            )
        return NotImplemented

    async def verify_file(self, file_path: Path) -> bool:
        """
        Verify that a file matches this checksum.

        Reads the file in 8KB chunks to handle large files (e.g., CUDA ~3GB)
        without loading the entire file into memory.

        Args:
            file_path: Path to the file to verify.

        Returns:
            True if the file's hash matches this checksum.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        import aiofiles

        hasher = hashlib.new(self.algorithm.value)
        async with aiofiles.open(file_path, "rb") as f:
            while True:
                chunk = await f.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)

        computed = hasher.hexdigest()
        return computed.lower() == self.value.lower()

    @classmethod
    def sha256(cls, hex_digest: str) -> Checksum:
        """Factory for SHA-256 checksums."""
        return cls(algorithm=HashAlgorithm.SHA256, value=hex_digest)

    @classmethod
    def md5(cls, hex_digest: str) -> Checksum:
        """Factory for MD5 checksums (legacy, prefer SHA-256)."""
        return cls(algorithm=HashAlgorithm.MD5, value=hex_digest)

    @classmethod
    async def compute_for_file(
        cls,
        file_path: Path,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    ) -> Checksum:
        """
        Compute the checksum of a file.

        Args:
            file_path: Path to the file.
            algorithm: Hash algorithm to use.

        Returns:
            Computed Checksum instance.
        """
        import aiofiles

        hasher = hashlib.new(algorithm.value)
        async with aiofiles.open(file_path, "rb") as f:
            while True:
                chunk = await f.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)

        return cls(algorithm=algorithm, value=hasher.hexdigest())
