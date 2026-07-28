"""
System detector port.

Abstract interface for detecting installed software, hardware
capabilities, and system state on the host machine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from src.core.enums import Architecture, GPUVendor
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version


@dataclass(frozen=True)
class DetectionResult:
    """Result of detecting a specific software package."""

    package_id: PackageId
    is_installed: bool
    version: Version | None = None
    install_path: Path | None = None
    detection_method: str = "unknown"
    confidence: float = 0.0


@dataclass(frozen=True)
class GPUInfo:
    """Detected GPU hardware information."""

    vendor: GPUVendor
    device_name: str
    driver_version: str | None = None
    vram_mb: int | None = None
    cuda_version: str | None = None
    compute_capability: str | None = None


@dataclass(frozen=True)
class SystemInfo:
    """Aggregate system information."""

    os_name: str
    os_version: str
    os_build: int
    architecture: Architecture
    total_ram_mb: int
    available_disk_gb: float
    gpus: list[GPUInfo]
    cpu_name: str
    cpu_cores: int


class SystemDetector(ABC):
    """
    Abstract interface for system detection capabilities.

    Detects installed software, GPU hardware, and OS information.
    Platform-specific implementations (Windows, Linux, macOS) provide
    the concrete behavior.
    """

    @abstractmethod
    async def detect_software(self, package_id: PackageId) -> DetectionResult:
        """
        Detect if a specific software package is installed.

        Uses a chain of detection strategies (registry → PATH →
        filesystem → version command) and returns the result with
        the highest confidence.

        Args:
            package_id: Package to look for.

        Returns:
            Detection result with version and install path if found.
        """

    @abstractmethod
    async def detect_all_installed(self) -> list[DetectionResult]:
        """
        Scan the system for all known DevForge-managed packages.

        Returns:
            List of detection results for all found software.
        """

    @abstractmethod
    async def detect_gpus(self) -> list[GPUInfo]:
        """
        Detect all GPU devices in the system.

        Returns:
            List of detected GPU information. Empty if no GPUs found.
        """

    @abstractmethod
    async def get_system_info(self) -> SystemInfo:
        """
        Collect aggregate system information.

        Returns:
            System information including OS, CPU, RAM, disk, and GPUs.
        """

    @abstractmethod
    async def check_path_entry(self, path: str) -> bool:
        """
        Check if a path entry exists in the system PATH.

        Args:
            path: Directory path to look for in PATH.

        Returns:
            True if the path is in the current PATH.
        """

    @abstractmethod
    async def get_path_entries(self) -> list[str]:
        """
        Get all entries in the system PATH.

        Returns:
            Ordered list of PATH entries.
        """
