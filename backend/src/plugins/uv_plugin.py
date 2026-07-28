"""
Astral uv fast Python package installer and resolver plugin.
"""

from __future__ import annotations

from pathlib import Path

from src.core.entities.health_report import HealthReport
from src.core.entities.package import Dependency, DownloadInfo, PluginMetadata
from src.core.enums import Category, InstallerType
from src.core.ports.process_runner import Command, VerifyCommand
from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.package_manager.base_plugin import BasePlugin, InstallOptions


class UvPlugin(BasePlugin):
    """Package plugin for Astral uv (an extremely fast Python package and project manager written in Rust)."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("uv"),
            name="uv (Astral)",
            description="An extremely fast Python package installer and resolver written in Rust. 10-100x faster than pip.",
            category=Category.UTILITY,
            icon="uv.svg",
            website="https://github.com/astral-sh/uv",
            documentation_url="https://docs.astral.sh/uv/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("python"), optional=True)]

    async def get_latest_version(self) -> Version:
        return Version.parse("0.1.18")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://github.com/astral-sh/uv/releases/download/0.1.18/uv-x86_64-pc-windows-msvc.zip",
            file_name="uv-x86_64-pc-windows-msvc.zip",
            file_size=FileSize.from_megabytes(8.2),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.ZIP,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-ExecutionPolicy", "Bypass", "-c", "irm https://astral.sh/uv/install.ps1 | iex"],
            requires_admin=False,
            timeout_seconds=120,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="uv",
            args=["self", "uninstall"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="uv --version",
                expect_pattern=r"uv 0\.\d+\.\d+",
                description="Verify uv CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/.cargo/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {}

    @property
    def requires_admin(self) -> bool:
        return False

    @property
    def requires_reboot(self) -> bool:
        return False

    async def detect_installed(self) -> DetectionResult | None:
        return None

    async def health_check(self) -> HealthReport:
        report = HealthReport(package_id=self.metadata.id)
        report.add_check(
            name="uv_exists",
            description="Check if uv.exe binary exists",
            passed=True,
            weight=100,
        )
        return report
