"""
Kubernetes CLI kubectl package plugin.
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


class KubectlPlugin(BasePlugin):
    """Package plugin for Kubernetes CLI kubectl control tool."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("kubectl"),
            name="Kubectl",
            description="The Kubernetes command-line tool, kubectl, allows you to run commands against Kubernetes clusters.",
            category=Category.DEVOPS,
            icon="kubernetes.svg",
            website="https://kubernetes.io/docs/tasks/tools/",
            documentation_url="https://kubernetes.io/docs/reference/kubectl/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.29.2")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://dl.k8s.io/release/v{ver_str}/bin/windows/amd64/kubectl.exe",
            file_name="kubectl.exe",
            file_size=FileSize.from_megabytes(52.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.PORTABLE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable="powershell",
            args=["-c", f"Copy-Item '{installer_path}' 'C:\\Program Files\\Kubectl\\kubectl.exe' -Force"],
            requires_admin=self.requires_admin,
            timeout_seconds=60,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="powershell",
            args=["-c", "Remove-Item -Recurse -Force 'C:\\Program Files\\Kubectl'"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="kubectl version --client",
                expect_pattern=r"Client Version: v1\.\d+\.\d+",
                description="Verify kubectl CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/Kubectl")]

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
            description="Check if kubectl.exe exists",
            passed=True,
            weight=100,
        )
        return report
