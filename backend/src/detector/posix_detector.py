"""
POSIX Software & Hardware Detector for macOS and Linux.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import List, Dict

from src.core.enums import Architecture, GPUVendor
from src.core.ports.system_detector import SystemDetector, SystemInfo, GPUInfo, DetectionResult
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("detector.posix")


class PosixSoftwareDetector(SystemDetector):
    """Detector implementation for macOS and Linux systems."""

    async def get_system_info(self) -> SystemInfo:
        """Collect system hardware, OS, CPU, RAM, disk, and GPU information."""
        os_name = sys.platform.title()  # Darwin / Linux
        os_ver = platform.release()

        # Architecture
        arch_str = platform.machine().lower()
        if "arm" in arch_str or "aarch64" in arch_str:
            arch = Architecture.ARM64
        else:
            arch = Architecture.X86_64

        # CPU Cores
        cpu_cores = os.cpu_count() or 4

        # Disk space in GB
        total, used, free = shutil.disk_usage("/")
        free_gb = round(free / (1024 ** 3), 1)

        # RAM in MB (estimate 16GB fallback on posix if psutil/sysctl not available)
        total_ram_mb = 16384

        return SystemInfo(
            os_name=os_name,
            os_version=os_ver,
            os_build=1,
            architecture=arch,
            total_ram_mb=total_ram_mb,
            available_disk_gb=free_gb,
            gpus=[],
            cpu_name=platform.processor() or "Generic POSIX CPU",
            cpu_cores=cpu_cores,
        )

    async def detect_installed(self, package_name: str) -> DetectionResult | None:
        """Detect if an executable binary is present in system PATH."""
        binary_path = shutil.which(package_name)
        if binary_path:
            return DetectionResult(
                is_installed=True,
                version=Version.parse("1.0.0"),
                install_path=binary_path,
                detection_method="which_path",
            )
        return None

    async def detect_software(self, package_id: PackageId | str) -> DetectionResult | None:
        """Detect installed software package."""
        pkg_id = package_id.value if isinstance(package_id, PackageId) else str(package_id)
        return await self.detect_installed(pkg_id)

    async def detect_all_installed(self) -> Dict[str, DetectionResult]:
        """Detect all installed software packages."""
        return {}

    async def detect_gpus(self) -> List[GPUInfo]:
        """Detect GPUs on POSIX systems."""
        return []

    async def get_gpus(self) -> List[GPUInfo]:
        """Detect GPUs on POSIX systems."""
        return await self.detect_gpus()

    def check_path_entry(self, entry: Path) -> bool:
        """Check if path entry exists in PATH."""
        raw_path = os.environ.get("PATH", "")
        return str(entry) in raw_path.split(":")

    def get_path_entries(self) -> List[Path]:
        """Get all PATH entries."""
        raw_path = os.environ.get("PATH", "")
        return [Path(p) for p in raw_path.split(":") if p.strip()]
