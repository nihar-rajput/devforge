"""
Registry accessor port.

Abstract interface for reading and writing to the Windows Registry.
Abstracted so the domain never depends on `winreg` directly,
and non-Windows platforms can provide no-op implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class RegistryAccessor(ABC):
    """
    Abstract interface for Windows Registry operations.

    All registry access goes through this port to maintain
    platform independence in the domain layer. The Windows
    implementation uses the `winreg` stdlib module.
    """

    @abstractmethod
    async def get_value(
        self,
        hive: str,
        key_path: str,
        value_name: str,
    ) -> str | int | None:
        """
        Read a value from the registry.

        Args:
            hive: Registry hive ('HKLM', 'HKCU', 'HCR').
            key_path: Path under the hive (e.g., 'SOFTWARE\\Python\\PythonCore').
            value_name: Name of the value to read.

        Returns:
            The value, or None if not found.
        """

    @abstractmethod
    async def set_value(
        self,
        hive: str,
        key_path: str,
        value_name: str,
        value: str | int,
        value_type: str = "REG_SZ",
    ) -> None:
        """
        Write a value to the registry.

        Args:
            hive: Registry hive.
            key_path: Path under the hive.
            value_name: Name of the value to set.
            value: The value to write.
            value_type: Registry value type ('REG_SZ', 'REG_EXPAND_SZ', 'REG_DWORD').
        """

    @abstractmethod
    async def key_exists(self, hive: str, key_path: str) -> bool:
        """Check if a registry key exists."""

    @abstractmethod
    async def enumerate_subkeys(self, hive: str, key_path: str) -> list[str]:
        """
        List all subkeys under a registry key.

        Args:
            hive: Registry hive.
            key_path: Path under the hive.

        Returns:
            List of subkey names.
        """

    @abstractmethod
    async def get_installed_programs(self) -> list[dict[str, str]]:
        """
        Read all installed programs from the standard Uninstall registry keys.

        Scans:
        - HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall
        - HKLM\\SOFTWARE\\WOW6432Node\\...\\Uninstall
        - HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall

        Returns:
            List of dicts with keys: 'DisplayName', 'DisplayVersion',
            'InstallLocation', 'UninstallString', 'Publisher'.
        """
