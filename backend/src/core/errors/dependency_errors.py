"""Dependency resolution errors."""

from __future__ import annotations

from src.core.errors.base import DevForgeError
from src.core.value_objects.package_id import PackageId


class DependencyResolutionError(DevForgeError):
    """Base error for dependency resolution failures."""


class CircularDependencyError(DependencyResolutionError):
    """Raised when a circular dependency is detected in the DAG."""

    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        cycle_str = " → ".join(cycle)
        super().__init__(
            f"Circular dependency detected: {cycle_str}",
            details="Review package dependency declarations to break the cycle.",
        )


class UnsatisfiedDependencyError(DependencyResolutionError):
    """Raised when a required dependency cannot be satisfied."""

    def __init__(
        self,
        package_id: PackageId,
        dependency_id: PackageId,
        constraint: str | None = None,
    ) -> None:
        msg = f"Package '{package_id}' requires '{dependency_id}'"
        if constraint:
            msg += f" ({constraint})"
        msg += " which cannot be satisfied"
        super().__init__(msg)


class DependencyConflictError(DependencyResolutionError):
    """Raised when two packages require incompatible versions of a dependency."""

    def __init__(
        self,
        dependency_id: PackageId,
        requester_a: PackageId,
        constraint_a: str,
        requester_b: PackageId,
        constraint_b: str,
    ) -> None:
        super().__init__(
            f"Version conflict for '{dependency_id}': "
            f"'{requester_a}' requires {constraint_a}, "
            f"'{requester_b}' requires {constraint_b}",
            details="These constraints cannot be satisfied simultaneously.",
        )
