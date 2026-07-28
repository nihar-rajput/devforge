"""
Installation repository port.

Abstract interface for persisting installation records (audit trail).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.core.entities.installation import Installation
from src.core.value_objects.package_id import PackageId


class InstallationRepository(ABC):
    """Abstract repository for Installation entity persistence."""

    @abstractmethod
    async def get_by_id(self, installation_id: UUID) -> Installation | None:
        """Retrieve an installation record by ID."""

    @abstractmethod
    async def get_by_package(self, package_id: PackageId) -> list[Installation]:
        """Retrieve all installation records for a package (history)."""

    @abstractmethod
    async def get_active(self) -> list[Installation]:
        """Retrieve all currently active (in-progress) installations."""

    @abstractmethod
    async def get_recent(self, limit: int = 50) -> list[Installation]:
        """Retrieve the most recent installation records."""

    @abstractmethod
    async def save(self, installation: Installation) -> None:
        """Persist an installation record (insert or update)."""

    @abstractmethod
    async def delete_older_than_days(self, days: int) -> int:
        """
        Delete installation records older than N days.

        Args:
            days: Records older than this many days are deleted.

        Returns:
            Number of records deleted.
        """
