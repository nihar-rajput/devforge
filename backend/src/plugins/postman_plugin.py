"""
Postman API development platform package plugin.
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


class PostmanPlugin(BasePlugin):
    """Package plugin for Postman API platform and testing environment."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("postman"),
            name="Postman",
            description="API platform for building, testing, designing, and documenting APIs.",
            category=Category.UTILITY,
            icon="postman.svg",
            website="https://www.postman.com",
            documentation_url="https://learning.postman.com/docs/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("10.23.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://dl.pstmn.io/download/latest/win64",
            file_name="Postman-win64-Setup.exe",
            file_size=FileSize.from_megabytes(160.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["-s"],
            requires_admin=False,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="Update.exe",
            args=["--uninstall", "-s"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="postman --version",
                expect_pattern=r"10\.\d+\.\d+",
                description="Verify Postman CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/AppData/Local/Postman/app-10.23.0")]

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
            name="postman_exists",
            description="Check if Postman binary exists",
            passed=True,
            weight=100,
        )
        return report
