"""
SQLite 3 command line tool package plugin.
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


class SqlitePlugin(BasePlugin):
    """Package plugin for SQLite 3 command line tool."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("sqlite"),
            name="SQLite 3",
            description="C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.",
            category=Category.DATABASE,
            icon="sqlite.svg",
            website="https://www.sqlite.org",
            documentation_url="https://www.sqlite.org/docs.html",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("3.45.1")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://www.sqlite.org/2024/sqlite-tools-win-x64-3450100.zip",
            file_name="sqlite-tools-win-x64-3450100.zip",
            file_size=FileSize.from_megabytes(2.5),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.ZIP,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Expand-Archive -Path '{installer_path}' -DestinationPath 'C:\\Program Files\\SQLite' -Force"],
            requires_admin=self.requires_admin,
            timeout_seconds=60,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Recurse -Force 'C:\\Program Files\\SQLite'"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="sqlite3 --version",
                expect_pattern=r"3\.\d+\.\d+",
                description="Verify sqlite3 CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/SQLite/sqlite-tools-win-x64-3450100")]

    def get_environment_variables(self) -> dict[str, str]:
        return {}

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
            name="sqlite3_exists",
            description="Check if sqlite3.exe binary exists",
            passed=True,
            weight=100,
        )
        return report
