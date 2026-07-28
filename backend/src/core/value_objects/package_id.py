"""
PackageId value object.

A strongly-typed identifier for packages, preventing accidental
use of raw strings where a package ID is expected.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PackageId(BaseModel):
    """
    Unique identifier for a package within the DevForge ecosystem.

    Package IDs are lowercase, alphanumeric strings with hyphens allowed.
    Examples: 'python', 'vs-code', 'cuda-toolkit', 'docker-desktop'.

    Using a value object instead of a raw string provides:
    - Type safety: can't accidentally pass a version string where an ID is expected
    - Validation: enforced format at construction time
    - Immutability: frozen model prevents accidental mutation
    """

    model_config = {"frozen": True}

    value: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-z][a-z0-9\-]*[a-z0-9]$|^[a-z]$",
        description="Lowercase identifier using alphanumerics and hyphens.",
    )

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PackageId):
            return self.value == other.value
        return NotImplemented

    @classmethod
    def of(cls, value: str) -> PackageId:
        """Factory method for concise construction."""
        return cls(value=value.lower().strip())
