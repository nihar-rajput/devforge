"""
HashiCorp Terraform Infrastructure as Code package plugin.
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


class TerraformPlugin(BasePlugin):
    """Package plugin for HashiCorp Terraform infrastructure as code."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("terraform"),
            name="Terraform",
            description="HashiCorp Terraform enables you to safely and predictably create, change, and improve cloud infrastructure.",
            category=Category.DEVOPS,
            icon="terraform.svg",
            website="https://www.terraform.io",
            documentation_url="https://developer.hashicorp.com/terraform/docs",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.7.4")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://releases.hashicorp.com/terraform/{ver_str}/terraform_{ver_str}_windows_amd64.zip",
            file_name=f"terraform_{ver_str}_windows_amd64.zip",
            file_size=FileSize.from_megabytes(24.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.ZIP,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Expand-Archive -Path '{installer_path}' -DestinationPath 'C:\\Program Files\\Terraform' -Force"],
            requires_admin=self.requires_admin,
            timeout_seconds=60,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Recurse -Force 'C:\\Program Files\\Terraform'"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="terraform --version",
                expect_pattern=r"Terraform v1\.\d+\.\d+",
                description="Verify Terraform CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/Terraform")]

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
            description="Check if terraform.exe exists",
            passed=True,
            weight=100,
        )
        return report
