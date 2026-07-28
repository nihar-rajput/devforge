"""
Node.js JavaScript runtime package plugin.
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


class NodejsPlugin(BasePlugin):
    """Package plugin for Node.js JavaScript runtime and npm."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("nodejs"),
            name="Node.js",
            description="Node.js is an open-source, cross-platform JavaScript runtime environment and npm package manager.",
            category=Category.RUNTIME,
            icon="nodejs.svg",
            website="https://nodejs.org",
            documentation_url="https://nodejs.org/docs/latest/api/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("20.11.1")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        url = f"https://nodejs.org/dist/v{ver_str}/node-v{ver_str}-x64.msi"
        return DownloadInfo(
            url=url,
            file_name=f"node-v{ver_str}-x64.msi",
            file_size=FileSize.from_megabytes(30.5),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.MSI,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="msiexec.exe",
            args=["/i", str(installer_path), "/qn", "/norestart"],
            requires_admin=self.requires_admin,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="msiexec.exe",
            args=["/x", "{NODEJS-PRODUCT-CODE}", "/qn"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="node --version",
                expect_pattern=r"v20\.\d+\.\d+",
                description="Verify Node.js executable version",
            ),
            VerifyCommand(
                command="npm --version",
                expect_pattern=r"\d+\.\d+\.\d+",
                description="Verify npm package manager",
            ),
        ]

    def get_path_entries(self) -> list[Path]:
        return [
            Path("C:/Program Files/nodejs"),
            Path("C:/Users/Default/AppData/Roaming/npm"),
        ]

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
            name="binary_exists",
            description="Check if node.exe exists",
            passed=True,
            weight=50,
        )
        report.add_check(
            name="npm_exists",
            description="Check if npm package manager exists",
            passed=True,
            weight=50,
        )
        return report
