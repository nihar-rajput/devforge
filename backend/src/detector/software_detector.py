"""
Software detector orchestrator implementation.

Implements SystemDetector port by running a multi-strategy detection chain:
RegistryScanner -> PathScanner -> FilesystemScanner -> VersionDetector.
"""

from __future__ import annotations

import os
import psutil
from typing import List

from src.core.enums import Architecture
from src.core.ports.system_detector import (
    DetectionResult,
    GPUInfo,
    SystemDetector,
    SystemInfo,
)
from src.core.value_objects.package_id import PackageId
from src.detector.filesystem_scanner import FilesystemScanner
from src.detector.gpu_detector import DefaultGPUDetector
from src.detector.path_scanner import PathScanner
from src.detector.registry_scanner import RegistryScanner
from src.detector.version_detector import VersionDetector
from src.logger.structured_logger import StructuredLogger
from src.system.path_manager import WindowsPathManager
from src.utils.platform_utils import get_architecture, get_os_build_number, get_os_name, get_os_version

logger = StructuredLogger("detector.software")


class DefaultSoftwareDetector(SystemDetector):
    """
    Concrete implementation of SystemDetector port interface.
    """

    def __init__(
        self,
        registry_scanner: RegistryScanner | None = None,
        path_scanner: PathScanner | None = None,
        filesystem_scanner: FilesystemScanner | None = None,
        version_detector: VersionDetector | None = None,
        gpu_detector: DefaultGPUDetector | None = None,
        path_manager: WindowsPathManager | None = None,
    ) -> None:
        self._registry_scanner = registry_scanner or RegistryScanner()
        self._path_scanner = path_scanner or PathScanner()
        self._filesystem_scanner = filesystem_scanner or FilesystemScanner()
        self._version_detector = version_detector or VersionDetector()
        self._gpu_detector = gpu_detector or DefaultGPUDetector()
        self._path_manager = path_manager or WindowsPathManager()

    async def detect_software(self, package_id: PackageId) -> DetectionResult:
        """
        Detect software installation using multi-strategy chain.
        Highest confidence result is returned.
        """
        pkg_name = package_id.value

        # Strategy 1: Registry scan (Confidence 0.9)
        reg_res = await self._registry_scanner.scan_package(package_id)
        if reg_res and reg_res.is_installed:
            return reg_res

        # Strategy 2: PATH scan (Confidence 0.8)
        path_res = await self._path_scanner.scan_executable(package_id, [pkg_name])
        if path_res and path_res.is_installed:
            # Enrich with version if possible
            ver = await self._version_detector.detect_version(f"{pkg_name} --version")
            return DetectionResult(
                package_id=package_id,
                is_installed=True,
                version=ver,
                install_path=path_res.install_path,
                detection_method="path",
                confidence=0.8,
            )

        # Strategy 3: Filesystem scan (Confidence 0.6)
        fs_res = await self._filesystem_scanner.scan_directories(package_id, [pkg_name, pkg_name.capitalize()])
        if fs_res and fs_res.is_installed:
            return fs_res

        # Not found
        return DetectionResult(
            package_id=package_id,
            is_installed=False,
            version=None,
            install_path=None,
            detection_method="none",
            confidence=0.0,
        )

    async def detect_all_installed(self) -> List[DetectionResult]:
        """
        Scan system for common developer packages.
        """
        common_packages = ["python", "git", "vscode", "nodejs", "docker", "cuda"]
        results: List[DetectionResult] = []
        for pkg_str in common_packages:
            res = await self.detect_software(PackageId.of(pkg_str))
            if res.is_installed:
                results.append(res)
        return results

    async def detect_gpus(self) -> List[GPUInfo]:
        return await self._gpu_detector.detect_gpus()

    async def get_system_info(self) -> SystemInfo:
        ram_bytes = psutil.virtual_memory().total
        ram_mb = int(ram_bytes / (1024 * 1024))

        # Disk space on C: drive
        disk_bytes = psutil.disk_usage("C:\\").free if os.name == "nt" else psutil.disk_usage("/").free
        disk_gb = round(disk_bytes / (1024 * 1024 * 1024), 2)

        gpus = await self.detect_gpus()

        return SystemInfo(
            os_name=get_os_name(),
            os_version=get_os_version(),
            os_build=get_os_build_number(),
            architecture=get_architecture(),
            total_ram_mb=ram_mb,
            available_disk_gb=disk_gb,
            gpus=gpus,
            cpu_name=psutil.cpu_freq().current if hasattr(psutil, "cpu_freq") else "CPU",
            cpu_cores=psutil.cpu_count(logical=True) or 4,
        )

    async def check_path_entry(self, path: str) -> bool:
        user_path = await self._path_manager.get_user_path()
        system_path = await self._path_manager.get_system_path()
        norm_path = os.path.normpath(path)
        return norm_path in [os.path.normpath(p) for p in user_path + system_path]

    async def get_path_entries(self) -> List[str]:
        return await self._path_manager.get_user_path() + await self._path_manager.get_system_path()
