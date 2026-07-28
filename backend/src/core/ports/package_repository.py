"""
Package repository port.

Abstract interface for persisting and querying Package entities.
The domain depends on this abstraction; the infrastructure layer
provides the concrete SQLite implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.entities.package import Package
from src.core.enums import Category, PackageStatus
from src.core.value_objects.package_id import PackageId


class PackageRepository(ABC):
    """
    Abstract repository for Package entity persistence.

    Implementations must handle serialization/deserialization between
    the domain entity and whatever storage backend is used.
    """

    @abstractmethod
    async def get_by_id(self, package_id: PackageId) -> Package | None:
        """
        Retrieve a package by its ID.

        Args:
            package_id: The package identifier.

        Returns:
            The package entity, or None if not found.
        """

    @abstractmethod
    async def get_all(self) -> list[Package]:
        """Retrieve all packages in the catalog."""

    @abstractmethod
    async def get_by_status(self, status: PackageStatus) -> list[Package]:
        """
        Retrieve all packages with a given status.

        Args:
            status: Filter packages by this status.

        Returns:
            List of matching packages.
        """

    @abstractmethod
    async def get_by_category(self, category: Category) -> list[Package]:
        """
        Retrieve all packages in a given category.

        Args:
            category: Filter packages by this category.

        Returns:
            List of matching packages.
        """

    @abstractmethod
    async def get_installed(self) -> list[Package]:
        """Retrieve all installed packages."""

    @abstractmethod
    async def save(self, package: Package) -> None:
        """
        Persist a package (insert or update).

        Args:
            package: The package entity to persist.
        """

    @abstractmethod
    async def delete(self, package_id: PackageId) -> None:
        """
        Remove a package from the catalog.

        Args:
            package_id: ID of the package to remove.
        """

    @abstractmethod
    async def search(self, query: str) -> list[Package]:
        """
        Search packages by name or description.

        Args:
            query: Search query string.

        Returns:
            List of matching packages, ordered by relevance.
        """

    @abstractmethod
    async def count(self, status: PackageStatus | None = None) -> int:
        """
        Count packages, optionally filtered by status.

        Args:
            status: Optional status filter.

        Returns:
            Number of matching packages.
        """
