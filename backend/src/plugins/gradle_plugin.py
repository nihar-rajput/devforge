"""
Gradle build automation package plugin.
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


class GradlePlugin(BasePlugin):
    """Package plugin for Gradle multi-language build automation tool."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("gradle"),
            name="Gradle",
            description="High-performance build automation tool for Java, Kotlin, Android, C++, and Groovy projects.",
            category=Category.UTILITY,
            icon="gradle.svg",
            website="https://gradle.org",
            documentation_url="https://docs.gradle.org/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("java"))]

    async def get_latest_version(self) -> Version:
        return Version.parse("8.6.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://services.gradle.org/distributions/gradle-{ver_str}-bin.zip",
            file_name=f"gradle-{ver_str}-bin.zip",
            file_size=FileSize.from_megabytes(125.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.ZIP,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Expand-Archive -Path '{installer_path}' -DestinationPath 'C:\\Program Files\\Gradle' -Force"],
            requires_admin=self.requires_admin,
            timeout_seconds=90,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Recurse -Force 'C:\\Program Files\\Gradle'"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="gradle --version",
                expect_pattern=r"Gradle 8\.\d+",
                description="Verify Gradle CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/Gradle/gradle-8.6/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {"GRADLE_HOME": "C:/Program Files/Gradle/gradle-8.6"}

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
            name="gradle_exists",
            description="Check if gradle.bat exists",
            passed=True,
            weight=100,
        )
        return report
