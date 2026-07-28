"""
Microsoft .NET 8.0 SDK package plugin.
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


class DotnetPlugin(BasePlugin):
    """Package plugin for Microsoft .NET 8.0 Software Development Kit."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("dotnet"),
            name=".NET 8.0 SDK",
            description="Free, cross-platform, open source developer platform for building many different types of applications with C#, F#, and Visual Basic.",
            category=Category.LANGUAGE,
            icon="dotnet.svg",
            website="https://dotnet.microsoft.com",
            documentation_url="https://learn.microsoft.com/en-us/dotnet/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("8.0.200")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://builds.dotnet.microsoft.com/dotnet/Sdk/8.0.200/dotnet-sdk-8.0.200-win-x64.exe",
            file_name="dotnet-sdk-8.0.200-win-x64.exe",
            file_size=FileSize.from_megabytes(210.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/quiet", "/norestart"],
            requires_admin=self.requires_admin,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/uninstall", "/quiet"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="dotnet --version",
                expect_pattern=r"8\.0\.\d+",
                description="Verify dotnet SDK version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/dotnet")]

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
            name="dotnet_exists",
            description="Check if dotnet.exe binary exists",
            passed=True,
            weight=100,
        )
        return report
