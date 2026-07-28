"""
DevForge Package Plugin Template.

Copy this file to create a new package plugin.
Every plugin must implement the BasePlugin abstract interface.
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


class TemplatePlugin(BasePlugin):
    """Reference plugin template. Replace TemplatePlugin with YourPackagePlugin."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("example-tool"),
            name="Example Developer Tool",
            description="A template package plugin demonstration.",
            category=Category.UTILITY,
            icon="example.svg",
            website="https://example.com",
            documentation_url="https://example.com/docs",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.0.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://example.com/download/example-installer.exe",
            file_name="example-installer.exe",
            file_size=FileSize.from_megabytes(25.0),
            checksum=Checksum.sha256("0000000000000000000000000000000000000000000000000000000000000000"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/VERYSILENT", "/NORESTART"],
            requires_admin=self.requires_admin,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="example-uninstall.exe",
            args=["/VERYSILENT"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="example --version",
                expect_pattern=r"1\.\d+\.\d+",
                description="Check example CLI binary version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/ExampleTool/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {"EXAMPLE_TOOL_HOME": "C:/Program Files/ExampleTool"}

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
            name="binary_exists",
            description="Check if main binary exists",
            passed=True,
            weight=100,
        )
        return report
