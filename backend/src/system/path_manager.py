"""
Windows PATH environment variable manager.

Implements PathManager port with atomic registry edits, deduplication,
shadowing conflict detection, backup/restore, and WM_SETTINGCHANGE broadcast.
"""

from __future__ import annotations

import os
from typing import List

from src.core.ports.path_manager import PathManager
from src.logger.structured_logger import StructuredLogger
from src.system.registry_manager import WindowsRegistryAccessor
from src.utils.platform_utils import is_windows

logger = StructuredLogger("system.path_manager")

if is_windows():
    import ctypes
else:
    ctypes = None  # type: ignore[assignment]


class WindowsPathManager(PathManager):
    """
    Concrete implementation of PathManager port for Windows.
    """

    def __init__(self, registry: WindowsRegistryAccessor | None = None) -> None:
        self._registry = registry or WindowsRegistryAccessor()

    async def get_user_path(self) -> List[str]:
        val = await self._registry.get_value("HKCU", "Environment", "PATH")
        if not val or not isinstance(val, str):
            return []
        return [p.strip() for p in val.split(";") if p.strip()]

    async def get_system_path(self) -> List[str]:
        val = await self._registry.get_value(
            "HKLM",
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            "PATH",
        )
        if not val or not isinstance(val, str):
            return []
        return [p.strip() for p in val.split(";") if p.strip()]

    async def add_to_path(
        self,
        entry: str,
        scope: str = "user",
        position: str = "append",
    ) -> bool:
        clean_entry = os.path.normpath(entry.strip())
        hive, key_path = self._get_scope_registry_key(scope)

        current_entries = (
            await self.get_user_path() if scope == "user" else await self.get_system_path()
        )
        norm_entries = [os.path.normpath(e) for e in current_entries]

        if clean_entry in norm_entries:
            logger.info(f"Entry '{clean_entry}' is already present in {scope} PATH.")
            return False

        if position == "prepend":
            new_entries = [clean_entry] + current_entries
        else:
            new_entries = current_entries + [clean_entry]

        new_val = ";".join(new_entries)

        await self._registry.set_value(
            hive, key_path, "PATH", new_val, value_type="REG_EXPAND_SZ"
        )
        await self.broadcast_change()

        # Also update current process environment
        os.environ["PATH"] = f"{os.environ.get('PATH', '')};{clean_entry}"
        logger.info(f"Added '{clean_entry}' to {scope} PATH.")
        return True

    async def remove_from_path(self, entry: str, scope: str = "user") -> bool:
        clean_entry = os.path.normpath(entry.strip())
        hive, key_path = self._get_scope_registry_key(scope)

        current_entries = (
            await self.get_user_path() if scope == "user" else await self.get_system_path()
        )
        filtered = [e for e in current_entries if os.path.normpath(e) != clean_entry]

        if len(filtered) == len(current_entries):
            return False

        new_val = ";".join(filtered)
        await self._registry.set_value(
            hive, key_path, "PATH", new_val, value_type="REG_EXPAND_SZ"
        )
        await self.broadcast_change()
        logger.info(f"Removed '{clean_entry}' from {scope} PATH.")
        return True

    async def find_conflicts(self, executable_name: str) -> List[str]:
        all_entries = await self.get_user_path() + await self.get_system_path()
        conflicts: List[str] = []

        target = executable_name.lower()
        if not target.endswith(".exe") and not target.endswith(".cmd") and not target.endswith(".bat"):
            targets = [f"{target}.exe", f"{target}.cmd", f"{target}.bat"]
        else:
            targets = [target]

        for entry in all_entries:
            if not os.path.exists(entry):
                continue
            for t in targets:
                exe_path = os.path.join(entry, t)
                if os.path.exists(exe_path):
                    conflicts.append(exe_path)
                    break

        return conflicts

    async def broadcast_change(self) -> None:
        if not is_windows():
            return

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002

        try:
            result = ctypes.c_long()
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                5000,
                ctypes.byref(result),
            )
            logger.debug("Broadcasted WM_SETTINGCHANGE environment update.")
        except Exception as exc:
            logger.warning(f"Failed to broadcast WM_SETTINGCHANGE: {exc}")

    async def backup_path(self, scope: str = "user") -> str:
        entries = await self.get_user_path() if scope == "user" else await self.get_system_path()
        return ";".join(entries)

    async def restore_path(self, backup: str, scope: str = "user") -> None:
        hive, key_path = self._get_scope_registry_key(scope)
        await self._registry.set_value(
            hive, key_path, "PATH", backup, value_type="REG_EXPAND_SZ"
        )
        await self.broadcast_change()

    def _get_scope_registry_key(self, scope: str) -> tuple[str, str]:
        if scope.lower() == "system":
            return "HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        return "HKCU", "Environment"
