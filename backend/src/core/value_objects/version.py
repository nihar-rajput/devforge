"""
Version value object.

Represents a semantic version with comparison operators and
compatibility checking for dependency resolution.
"""

from __future__ import annotations

import re
from functools import total_ordering

from pydantic import BaseModel, Field, model_validator


_SEMVER_PATTERN = re.compile(
    r"^(?P<major>0|[1-9]\d*)"
    r"\.(?P<minor>0|[1-9]\d*)"
    r"\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<pre>[0-9A-Za-z\-.]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z\-.]+))?$"
)


@total_ordering
class Version(BaseModel):
    """
    Semantic version following SemVer 2.0.0 specification.

    Supports comparison operators for dependency constraint resolution.
    Pre-release versions sort before their release counterpart.

    Examples:
        Version.parse("3.12.1")
        Version.parse("2.0.0-beta.1")
        Version(major=3, minor=12, patch=1)
    """

    model_config = {"frozen": True}

    major: int = Field(..., ge=0, description="Major version (breaking changes).")
    minor: int = Field(..., ge=0, description="Minor version (new features).")
    patch: int = Field(..., ge=0, description="Patch version (bug fixes).")
    pre_release: str | None = Field(
        default=None,
        description="Pre-release label (e.g., 'beta.1', 'rc.2').",
    )
    build_metadata: str | None = Field(
        default=None,
        description="Build metadata (ignored in comparisons).",
    )

    @classmethod
    def parse(cls, version_string: str) -> Version:
        """
        Parse a version string into a Version object.

        Args:
            version_string: A string like '3.12.1', '2.0.0-beta.1+build.42'.

        Returns:
            Parsed Version instance.

        Raises:
            ValueError: If the string does not match semantic version format.
        """
        cleaned = version_string.strip().lstrip("v")
        match = _SEMVER_PATTERN.match(cleaned)
        if not match:
            raise ValueError(
                f"Invalid semantic version: '{version_string}'. "
                f"Expected format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]"
            )
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            pre_release=match.group("pre"),
            build_metadata=match.group("build"),
        )

    @model_validator(mode="after")
    def _validate_components(self) -> Version:
        """Ensure pre-release and build metadata don't contain invalid chars."""
        if self.pre_release and not re.match(r"^[0-9A-Za-z\-.]+$", self.pre_release):
            raise ValueError(f"Invalid pre-release identifier: '{self.pre_release}'")
        if self.build_metadata and not re.match(r"^[0-9A-Za-z\-.]+$", self.build_metadata):
            raise ValueError(f"Invalid build metadata: '{self.build_metadata}'")
        return self

    @property
    def _comparison_tuple(self) -> tuple[int, int, int, bool, str]:
        """
        Tuple for comparison. Pre-release versions sort BEFORE their
        corresponding release version (per SemVer spec).
        """
        return (
            self.major,
            self.minor,
            self.patch,
            self.pre_release is None,  # True (1) sorts after False (0)
            self.pre_release or "",
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._comparison_tuple == other._comparison_tuple
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._comparison_tuple < other._comparison_tuple
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._comparison_tuple)

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version

    def is_compatible_with(self, constraint: str) -> bool:
        """
        Check if this version satisfies a constraint string.

        Supported operators: >=, <=, >, <, ==, !=, ~= (compatible release).

        Args:
            constraint: Version constraint like '>=3.10.0', '~=3.12.0'.

        Returns:
            True if this version satisfies the constraint.
        """
        constraint = constraint.strip()
        match = re.match(r"^(>=|<=|>|<|==|!=|~=)\s*(.+)$", constraint)
        if not match:
            raise ValueError(f"Invalid version constraint: '{constraint}'")

        operator, version_str = match.group(1), match.group(2)
        other = Version.parse(version_str)

        if operator == ">=":
            return self >= other
        elif operator == "<=":
            return self <= other
        elif operator == ">":
            return self > other
        elif operator == "<":
            return self < other
        elif operator == "==":
            return self == other
        elif operator == "!=":
            return self != other
        elif operator == "~=":
            # Compatible release: ~=3.12.0 means >=3.12.0 and <3.13.0
            upper = Version(major=other.major, minor=other.minor + 1, patch=0)
            return self >= other and self < upper
        else:
            raise ValueError(f"Unsupported version operator: '{operator}'")
