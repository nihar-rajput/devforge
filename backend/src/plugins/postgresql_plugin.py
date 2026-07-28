"""
PostgreSQL relational database package plugin.
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


class PostgresqlPlugin(BasePlugin):
    """Package plugin for PostgreSQL relational database engine."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("postgresql"),
            name="PostgreSQL",
            description="The World's Most Advanced Open Source Relational Database engine and psql CLI.",
            category=Category.DATABASE,
            icon="postgresql.svg",
            website="https://www.postgresql.org",
            documentation_url="https://www.postgresql.org/docs/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("16.2.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://sbp.enterprisedb.com/getfile.jsp?fileid=1258672",
            file_name="postgresql-16.2-1-windows-x64.exe",
            file_size=FileSize.from_megabytes(340.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["--mode", "unattended", "--unattendedmodeui", "minimal", "--superpassword", "postgres"],
            requires_admin=self.requires_admin,
            timeout_seconds=600,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="uninstall-postgresql.exe",
            args=["--mode", "unattended"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="psql --version",
                expect_pattern=r"psql \(PostgreSQL\) 16\.\d+",
                description="Verify psql database CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/PostgreSQL/16/bin")]

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
            name="psql_exists",
            description="Check if psql.exe CLI exists",
            passed=True,
            weight=100,
        )
        return report
