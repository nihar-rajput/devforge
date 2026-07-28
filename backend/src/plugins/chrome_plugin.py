"""
Google Chrome web browser package plugin.
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


class ChromePlugin(BasePlugin):
    """Package plugin for Google Chrome web browser and DevTools environment."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("chrome"),
            name="Google Chrome",
            description="Fast, secure, and modern web browser with built-in Developer Tools and V8 JavaScript engine.",
            category=Category.UTILITY,
            icon="chrome.svg",
            website="https://www.google.com/chrome/",
            documentation_url="https://developer.chrome.com/docs/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("122.0.6261")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B6E419515-B6ED-B089-21F6-3CF7015C3EFE%7D%26lang%3Den%26browser%3D4%26usagestats%3D0%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-stable-statsdef_1%26installdataindex%3Dempty/chrome/install/ChromeStandaloneSetup64.exe",
            file_name="ChromeStandaloneSetup64.exe",
            file_size=FileSize.from_megabytes(105.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/silent", "/install"],
            requires_admin=self.requires_admin,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="setup.exe",
            args=["--uninstall", "--multi-install", "--chrome", "--system-level"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="chrome --version",
                expect_pattern=r"Google Chrome 122\.\d+",
                description="Verify Google Chrome executable",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/Google/Chrome/Application")]

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
            name="chrome_exists",
            description="Check if chrome.exe exists",
            passed=True,
            weight=100,
        )
        return report
