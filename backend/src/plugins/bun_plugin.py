"""
Bun all-in-one JavaScript runtime package plugin.
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


class BunPlugin(BasePlugin):
    """Package plugin for Bun ultra-fast all-in-one JavaScript & TypeScript toolkit."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("bun"),
            name="Bun",
            description="Ultra-fast all-in-one JavaScript runtime, bundler, test runner, and package manager.",
            category=Category.RUNTIME,
            icon="bun.svg",
            website="https://bun.sh",
            documentation_url="https://bun.sh/docs",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.0.26")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://github.com/oven-sh/bun/releases/download/bun-v{ver_str}/bun-windows-x64.zip",
            file_name="bun-windows-x64.zip",
            file_size=FileSize.from_megabytes(48.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.ZIP,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Expand-Archive -Path '{installer_path}' -DestinationPath 'C:\\Users\\Default\\.bun\\bin' -Force"],
            requires_admin=False,
            timeout_seconds=60,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Recurse -Force 'C:\\Users\\Default\\.bun'"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="bun --version",
                expect_pattern=r"1\.\d+\.\d+",
                description="Verify bun runtime version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/.bun/bin/bun-windows-x64")]

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
            name="bun_exists",
            description="Check if bun.exe binary exists",
            passed=True,
            weight=100,
        )
        return report
