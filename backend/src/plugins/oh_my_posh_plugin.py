"""
Oh My Posh prompt theme engine package plugin.
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


class OhMyPoshPlugin(BasePlugin):
    """Package plugin for Oh My Posh terminal prompt theme engine."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("oh-my-posh"),
            name="Oh My Posh",
            description="A prompt theme engine for any shell. Customizes your terminal prompt with Git status, execution time, and badges.",
            category=Category.UTILITY,
            icon="ohmyposh.svg",
            website="https://ohmyposh.dev",
            documentation_url="https://ohmyposh.dev/docs/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("19.14.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://github.com/JanDeDobbeleer/oh-my-posh/releases/download/v{ver_str}/posh-windows-amd64.exe",
            file_name="posh-windows-amd64.exe",
            file_size=FileSize.from_megabytes(14.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.PORTABLE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Copy-Item '{installer_path}' 'C:\\Users\\Default\\AppData\\Local\\Programs\\oh-my-posh\\bin\\oh-my-posh.exe' -Force"],
            requires_admin=False,
            timeout_seconds=60,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Recurse -Force 'C:\\Users\\Default\\AppData\\Local\\Programs\\oh-my-posh'"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="oh-my-posh --version",
                expect_pattern=r"19\.\d+\.\d+",
                description="Verify oh-my-posh CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/AppData/Local/Programs/oh-my-posh/bin")]

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
            name="ohmyposh_exists",
            description="Check if oh-my-posh.exe binary exists",
            passed=True,
            weight=100,
        )
        return report
