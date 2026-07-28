"""
PATH repairer implementation.
"""

from __future__ import annotations

from src.package_manager.base_plugin import BasePlugin
from src.system.path_manager import WindowsPathManager


class PathRepairer:
    """
    Repairs missing PATH environment variable entries for a package.
    """

    def __init__(self, path_manager: WindowsPathManager | None = None) -> None:
        self._path_manager = path_manager or WindowsPathManager()

    async def repair_path(self, plugin: BasePlugin) -> int:
        """
        Verify and restore missing PATH entries for plugin.

        Returns:
            Number of restored PATH entries.
        """
        paths = plugin.get_path_entries()
        restored = 0

        user_path = await self._path_manager.get_user_path()
        system_path = await self._path_manager.get_system_path()
        current = user_path + system_path

        for p in paths:
            p_str = str(p)
            if p_str not in current:
                added = await self._path_manager.add_to_path(p_str, scope="user")
                if added:
                    restored += 1

        return restored
