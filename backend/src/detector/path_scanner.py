"""
PATH scanner for detecting installed software executables on system PATH.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.package_id import PackageId
from src.system.path_manager import WindowsPathManager


class PathScanner:
    """
    Scans environment PATH entries to find package binary executables.
    """

    def __init__(self, path_manager: WindowsPathManager | None = None) -> None:
        self._path_manager = path_manager or WindowsPathManager()

    async def scan_executable(
        self,
        package_id: PackageId,
        executable_names: List[str],
    ) -> DetectionResult | None:
        """
        Scan PATH entries for the specified binary executable names.
        """
        for exe in executable_names:
            matches = await self._path_manager.find_conflicts(exe)
            if matches:
                exe_path = Path(matches[0])
                return DetectionResult(
                    package_id=package_id,
                    is_installed=True,
                    version=None,  # Version detector will extract actual version
                    install_path=exe_path.parent,
                    detection_method="path",
                    confidence=0.8,
                )

        return None
