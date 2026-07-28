"""
Filesystem scanner for probing common Windows install directories.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.package_id import PackageId


class FilesystemScanner:
    """
    Probes standard Windows installation locations for package directories.
    """

    COMMON_PATHS = [
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path(os.path.expandvars("%LOCALAPPDATA%/Programs")),
        Path(os.path.expandvars("%APPDATA%")),
    ]

    async def scan_directories(
        self,
        package_id: PackageId,
        dir_names: List[str],
    ) -> DetectionResult | None:
        """
        Probe common installation paths for matching directory names.
        """
        for base in self.COMMON_PATHS:
            if not base.exists():
                continue
            for target_name in dir_names:
                target_path = base / target_name
                if target_path.exists() and target_path.is_dir():
                    return DetectionResult(
                        package_id=package_id,
                        is_installed=True,
                        version=None,
                        install_path=target_path,
                        detection_method="filesystem",
                        confidence=0.6,
                    )

        return None
