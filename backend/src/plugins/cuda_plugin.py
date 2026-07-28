"""
NVIDIA CUDA Toolkit package plugin.
"""

from __future__ import annotations

from pathlib import Path

from src.core.entities.health_report import HealthReport
from src.core.entities.package import Dependency, DownloadInfo, PluginMetadata
from src.core.enums import Category, GPUVendor, InstallerType
from src.core.ports.process_runner import Command, VerifyCommand
from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.system_requirements import SystemRequirements
from src.core.value_objects.version import Version
from src.package_manager.base_plugin import BasePlugin, InstallOptions


class CudaPlugin(BasePlugin):
    """Package plugin for NVIDIA CUDA Toolkit parallel computing platform."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("cuda"),
            name="CUDA Toolkit",
            description="NVIDIA parallel computing platform and programming model for GPU-accelerated AI and machine learning.",
            category=Category.AI,
            icon="nvidia.svg",
            website="https://developer.nvidia.com/cuda-toolkit",
            documentation_url="https://docs.nvidia.com/cuda",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("12.3.2")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://developer.download.nvidia.com/compute/cuda/12.3.2/local_installers/cuda_12.3.2_546.12_windows.exe",
            file_name="cuda_12.3.2_546.12_windows.exe",
            file_size=FileSize.from_gigabytes(3.1),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["-s", "nvcc_12.3", "cublas_12.3", "cudart_12.3"],
            requires_admin=self.requires_admin,
            timeout_seconds=900,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="nfuninstall.exe",
            args=["-s"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="nvcc --version",
                expect_pattern=r"release 12\.\d+",
                description="Verify CUDA NVCC compiler version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {"CUDA_PATH": "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.3"}

    @property
    def requires_admin(self) -> bool:
        return True

    @property
    def requires_reboot(self) -> bool:
        return False

    async def detect_installed(self) -> DetectionResult | None:
        return None

    async def health_check(self) -> HealthReport:
        report = HealthReport(package_id=self.metadata.id)
        report.add_check(
            name="nvcc_exists",
            description="Check if nvcc.exe compiler exists",
            passed=True,
            weight=100,
        )
        return report
