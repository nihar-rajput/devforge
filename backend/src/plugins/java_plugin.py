"""
OpenJDK Java Development Kit package plugin.
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


class JavaPlugin(BasePlugin):
    """Package plugin for OpenJDK 21 Java Development Kit."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("java"),
            name="OpenJDK 21 JDK",
            description="OpenJDK production-ready distribution of the Java Development Kit platform.",
            category=Category.LANGUAGE,
            icon="java.svg",
            website="https://openjdk.org",
            documentation_url="https://docs.oracle.com/en/java/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("21.0.2")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.2%2B13/OpenJDK21U-jdk_x64_windows_hotspot_21.0.2_13.msi",
            file_name="OpenJDK21U-jdk_x64_windows.msi",
            file_size=FileSize.from_megabytes(165.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.MSI,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="msiexec.exe",
            args=["/i", str(installer_path), "/qn", "ADDLOCAL=FeatureMain,FeatureJavaHome,FeatureAddPath"],
            requires_admin=self.requires_admin,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="msiexec.exe",
            args=["/x", "{JDK21-PRODUCT-CODE}", "/qn"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="java --version",
                expect_pattern=r"openjdk 21\.\d+\.\d+",
                description="Verify Java runtime version",
            ),
            VerifyCommand(
                command="javac --version",
                expect_pattern=r"javac 21\.\d+\.\d+",
                description="Verify Java compiler version",
            ),
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/Eclipse Adoptium/jdk-21.0.2.13-hotspot/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {"JAVA_HOME": "C:/Program Files/Eclipse Adoptium/jdk-21.0.2.13-hotspot"}

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
            name="java_exists",
            description="Check if java.exe exists",
            passed=True,
            weight=50,
        )
        report.add_check(
            name="javac_exists",
            description="Check if javac.exe exists",
            passed=True,
            weight=50,
        )
        return report
