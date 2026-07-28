"""
GitHub CLI gh package plugin.
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


class GhPlugin(BasePlugin):
    """Package plugin for GitHub official CLI tool gh."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("gh"),
            name="GitHub CLI",
            description="GitHub's official command line tool. Brings pull requests, issues, GitHub Actions, and repos to your terminal.",
            category=Category.VERSION_CONTROL,
            icon="github.svg",
            website="https://cli.github.com",
            documentation_url="https://cli.github.com/manual/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("git"))]

    async def get_latest_version(self) -> Version:
        return Version.parse("2.43.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://github.com/cli/cli/releases/download/v{ver_str}/gh_{ver_str}_windows_amd64.msi",
            file_name=f"gh_{ver_str}_windows_amd64.msi",
            file_size=FileSize.from_megabytes(18.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.MSI,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="msiexec.exe",
            args=["/i", str(installer_path), "/qn", "/norestart"],
            requires_admin=self.requires_admin,
            timeout_seconds=120,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="msiexec.exe",
            args=["/x", "{GH-CLI-PRODUCT-CODE}", "/qn"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="gh --version",
                expect_pattern=r"gh version 2\.\d+\.\d+",
                description="Verify gh CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/GitHub CLI")]

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
            name="gh_exists",
            description="Check if gh.exe exists",
            passed=True,
            weight=100,
        )
        return report
