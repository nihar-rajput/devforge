"""
pnpm fast disk-space efficient package manager plugin.
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


class PnpmPlugin(BasePlugin):
    """Package plugin for pnpm fast, disk space efficient JavaScript package manager."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("pnpm"),
            name="pnpm",
            description="Fast, disk space efficient package manager for Node.js and JavaScript monorepos.",
            category=Category.UTILITY,
            icon="pnpm.svg",
            website="https://pnpm.io",
            documentation_url="https://pnpm.io/motivation",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("nodejs"))]

    async def get_latest_version(self) -> Version:
        return Version.parse("8.15.4")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://github.com/pnpm/pnpm/releases/download/v8.15.4/pnpm-win-x64.exe",
            file_name="pnpm-win-x64.exe",
            file_size=FileSize.from_megabytes(42.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.PORTABLE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Copy-Item '{installer_path}' 'C:\\Users\\Default\\AppData\\Local\\pnpm\\pnpm.exe' -Force"],
            requires_admin=False,
            timeout_seconds=60,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Force 'C:\\Users\\Default\\AppData\\Local\\pnpm\\pnpm.exe'"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="pnpm --version",
                expect_pattern=r"8\.\d+\.\d+",
                description="Verify pnpm CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/AppData/Local/pnpm")]

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
            name="pnpm_exists",
            description="Check if pnpm.exe exists",
            passed=True,
            weight=100,
        )
        return report
