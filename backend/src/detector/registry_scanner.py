"""
Windows Registry scanner for installed software detection.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.system.registry_manager import WindowsRegistryAccessor


class RegistryScanner:
    """
    Scans Windows Uninstall registry keys to detect installed software packages.
    """

    def __init__(self, registry: WindowsRegistryAccessor | None = None) -> None:
        self._registry = registry or WindowsRegistryAccessor()

    async def scan_package(
        self,
        package_id: PackageId,
        search_terms: List[str] | None = None,
    ) -> DetectionResult | None:
        """
        Scan registry for a package by ID or matching search terms.
        """
        terms = search_terms or [package_id.value.replace("-", " "), package_id.value]
        programs = await self._registry.get_installed_programs()

        for prog in programs:
            display_name = prog.get("DisplayName", "").lower()
            for term in terms:
                if term.lower() in display_name:
                    version_str = prog.get("DisplayVersion")
                    install_loc = prog.get("InstallLocation")

                    version = None
                    if version_str:
                        # Extract semver pattern
                        match = re.search(r"(\d+\.\d+(?:\.\d+)?)", version_str)
                        if match:
                            try:
                                v_raw = match.group(1)
                                if v_raw.count(".") == 1:
                                    v_raw += ".0"
                                version = Version.parse(v_raw)
                            except ValueError:
                                pass

                    return DetectionResult(
                        package_id=package_id,
                        is_installed=True,
                        version=version,
                        install_path=Path(install_loc) if install_loc else None,
                        detection_method="registry",
                        confidence=0.9,
                    )

        return None
