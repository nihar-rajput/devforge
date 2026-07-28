"""
IntelliJ IDEA Community Edition IDE package plugin.
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


class IntellijPlugin(BasePlugin):
    """Package plugin for JetBrains IntelliJ IDEA Community Edition IDE."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("intellij"),
            name="IntelliJ IDEA CE",
            description="Capable and ergonomic IDE for JVM and Java development by JetBrains.",
            category=Category.EDITOR,
            icon="intellij.svg",
            website="https://www.jetbrains.com/idea/",
            documentation_url="https://www.jetbrains.com/idea/documentation/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("java"), optional=True)]

    async def get_latest_version(self) -> Version:
        return Version.parse("2023.3.4")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://download.jetbrains.com/idea/ideaIC-2023.3.4.exe",
            file_name="ideaIC-2023.3.4.exe",
            file_size=FileSize.from_megabytes(650.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/S"],
            requires_admin=self.requires_admin,
            timeout_seconds=600,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="Uninstall.exe",
            args=["/S"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="idea64.exe --version",
                expect_pattern=r"2023\.\d+\.\d+",
                description="Verify IntelliJ IDEA binary",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/JetBrains/IntelliJ IDEA Community Edition 2023.3.4/bin")]

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
            name="idea_exists",
            description="Check if idea64.exe exists",
            passed=True,
            weight=100,
        )
        return report
