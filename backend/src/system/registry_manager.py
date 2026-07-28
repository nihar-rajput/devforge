"""
Windows Registry Accessor implementation.

Implements RegistryAccessor port interface using the winreg stdlib module.
"""

from __future__ import annotations

from typing import Any, List

from src.config.constants import UNINSTALL_REGISTRY_PATHS
from src.core.ports.registry_accessor import RegistryAccessor
from src.logger.structured_logger import StructuredLogger
from src.utils.platform_utils import is_windows

logger = StructuredLogger("system.registry")

if is_windows():
    import winreg
else:
    winreg = None  # type: ignore[assignment]


class WindowsRegistryAccessor(RegistryAccessor):
    """
    Concrete implementation of RegistryAccessor port using Python's winreg.
    Supports reading, writing, key enumeration, and installed programs scanning.
    """

    HIVE_MAP = {
        "HKLM": getattr(winreg, "HKEY_LOCAL_MACHINE", None),
        "HKCU": getattr(winreg, "HKEY_CURRENT_USER", None),
        "HCR": getattr(winreg, "HKEY_CLASSES_ROOT", None),
    }

    TYPE_MAP = {
        "REG_SZ": getattr(winreg, "REG_SZ", 1),
        "REG_EXPAND_SZ": getattr(winreg, "REG_EXPAND_SZ", 2),
        "REG_DWORD": getattr(winreg, "REG_DWORD", 4),
    }

    def _get_hive(self, hive_str: str) -> Any:
        hive = self.HIVE_MAP.get(hive_str.upper())
        if hive is None:
            raise ValueError(f"Invalid or unsupported registry hive: '{hive_str}'")
        return hive

    async def get_value(
        self,
        hive: str,
        key_path: str,
        value_name: str,
    ) -> str | int | None:
        if not is_windows():
            return None

        try:
            hkey = self._get_hive(hive)
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, value_name)
                return val
        except FileNotFoundError:
            return None
        except Exception as exc:
            logger.debug(f"Registry get_value error for {hive}\\{key_path}\\{value_name}: {exc}")
            return None

    async def set_value(
        self,
        hive: str,
        key_path: str,
        value_name: str,
        value: str | int,
        value_type: str = "REG_SZ",
    ) -> None:
        if not is_windows():
            return

        hkey = self._get_hive(hive)
        reg_type = self.TYPE_MAP.get(value_type, winreg.REG_SZ)

        with winreg.CreateKeyEx(hkey, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, value_name, 0, reg_type, value)

    async def key_exists(self, hive: str, key_path: str) -> bool:
        if not is_windows():
            return False

        try:
            hkey = self._get_hive(hive)
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ):
                return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    async def enumerate_subkeys(self, hive: str, key_path: str) -> List[str]:
        if not is_windows():
            return []

        subkeys: List[str] = []
        try:
            hkey = self._get_hive(hive)
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ) as key:
                count, _, _ = winreg.QueryInfoKey(key)
                for i in range(count):
                    name = winreg.EnumKey(key, i)
                    subkeys.append(name)
        except Exception as exc:
            logger.debug(f"Failed to enumerate subkeys for {hive}\\{key_path}: {exc}")

        return subkeys

    async def get_installed_programs(self) -> List[dict[str, str]]:
        if not is_windows():
            return []

        installed: List[dict[str, str]] = []

        for hive, path in UNINSTALL_REGISTRY_PATHS:
            subkeys = await self.enumerate_subkeys(hive, path)
            for subkey_name in subkeys:
                full_path = f"{path}\\{subkey_name}"
                display_name = await self.get_value(hive, full_path, "DisplayName")
                if display_name and isinstance(display_name, str):
                    display_version = await self.get_value(hive, full_path, "DisplayVersion")
                    install_loc = await self.get_value(hive, full_path, "InstallLocation")
                    uninstall_str = await self.get_value(hive, full_path, "UninstallString")
                    publisher = await self.get_value(hive, full_path, "Publisher")

                    installed.append({
                        "DisplayName": display_name,
                        "DisplayVersion": str(display_version) if display_version else "",
                        "InstallLocation": str(install_loc) if install_loc else "",
                        "UninstallString": str(uninstall_str) if uninstall_str else "",
                        "Publisher": str(publisher) if publisher else "",
                        "RegistryHive": hive,
                        "RegistryKey": full_path,
                    })

        return installed
