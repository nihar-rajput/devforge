"""
FileSize value object.

Provides human-readable file size formatting and comparison,
used for download progress display and disk usage tracking.
"""

from __future__ import annotations

from functools import total_ordering

from pydantic import BaseModel, Field


@total_ordering
class FileSize(BaseModel):
    """
    Represents a file size in bytes with human-readable formatting.

    Usage:
        size = FileSize(bytes_count=1_073_741_824)
        str(size)  # "1.00 GB"
        size.megabytes  # 1024.0
    """

    model_config = {"frozen": True}

    bytes_count: int = Field(..., ge=0, description="Size in bytes.")

    _UNITS: list[tuple[str, int]] = [
        ("TB", 1 << 40),
        ("GB", 1 << 30),
        ("MB", 1 << 20),
        ("KB", 1 << 10),
        ("B", 1),
    ]

    @property
    def kilobytes(self) -> float:
        """Size in kilobytes."""
        return self.bytes_count / 1024

    @property
    def megabytes(self) -> float:
        """Size in megabytes."""
        return self.bytes_count / (1024 * 1024)

    @property
    def gigabytes(self) -> float:
        """Size in gigabytes."""
        return self.bytes_count / (1024 * 1024 * 1024)

    def __str__(self) -> str:
        if self.bytes_count == 0:
            return "0 B"
        for unit_name, unit_size in self._UNITS:
            if self.bytes_count >= unit_size:
                value = self.bytes_count / unit_size
                return f"{value:.2f} {unit_name}"
        return f"{self.bytes_count} B"

    def __hash__(self) -> int:
        return hash(self.bytes_count)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FileSize):
            return self.bytes_count == other.bytes_count
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, FileSize):
            return self.bytes_count < other.bytes_count
        return NotImplemented

    @classmethod
    def from_megabytes(cls, mb: float) -> FileSize:
        """Create from megabytes."""
        return cls(bytes_count=int(mb * 1024 * 1024))

    @classmethod
    def from_gigabytes(cls, gb: float) -> FileSize:
        """Create from gigabytes."""
        return cls(bytes_count=int(gb * 1024 * 1024 * 1024))

    @classmethod
    def zero(cls) -> FileSize:
        """Create a zero-sized FileSize."""
        return cls(bytes_count=0)
