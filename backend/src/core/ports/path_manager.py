"""
PATH manager port.

Abstract interface for reading and modifying the system PATH
environment variable with atomic operations and broadcast.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PathManager(ABC):
    """
    Abstract interface for PATH environment variable management.

    The Windows implementation modifies the registry directly and
    broadcasts WM_SETTINGCHANGE to notify running processes.
    Includes conflict detection and deduplication.
    """

    @abstractmethod
    async def get_user_path(self) -> list[str]:
        """Get the current user-scope PATH entries."""

    @abstractmethod
    async def get_system_path(self) -> list[str]:
        """Get the current system-scope PATH entries (requires admin to modify)."""

    @abstractmethod
    async def add_to_path(
        self,
        entry: str,
        scope: str = "user",
        position: str = "append",
    ) -> bool:
        """
        Add a directory to the PATH.

        Deduplicates automatically. Broadcasts environment change
        notification to all running processes.

        Args:
            entry: Directory path to add.
            scope: 'user' or 'system'. System requires admin.
            position: 'append' or 'prepend'.

        Returns:
            True if the entry was added, False if it already existed.
        """

    @abstractmethod
    async def remove_from_path(self, entry: str, scope: str = "user") -> bool:
        """
        Remove a directory from the PATH.

        Args:
            entry: Directory path to remove.
            scope: 'user' or 'system'.

        Returns:
            True if the entry was removed, False if it wasn't found.
        """

    @abstractmethod
    async def find_conflicts(self, executable_name: str) -> list[str]:
        """
        Find PATH entries that contain the same executable name.

        Detects shadowing issues (e.g., Python 3.11 before Python 3.12).

        Args:
            executable_name: Name of the executable to search for.

        Returns:
            List of PATH entries containing the executable.
        """

    @abstractmethod
    async def broadcast_change(self) -> None:
        """
        Notify all running processes that environment variables have changed.

        On Windows, this sends WM_SETTINGCHANGE via SendMessageTimeout.
        """

    @abstractmethod
    async def backup_path(self, scope: str = "user") -> str:
        """
        Create a backup of the current PATH value.

        Returns:
            The full PATH string for rollback purposes.
        """

    @abstractmethod
    async def restore_path(self, backup: str, scope: str = "user") -> None:
        """
        Restore PATH from a backup.

        Args:
            backup: Previously backed-up PATH string.
            scope: 'user' or 'system'.
        """
