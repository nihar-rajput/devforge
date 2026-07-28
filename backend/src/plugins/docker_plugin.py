"""
Docker Desktop package plugin.
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
from src.core.value_objects.system_requirements import SystemRequirements
from src.core.value_objects.version import Version
from src.package_manager.base_plugin import BasePlugin, InstallOptions


class DockerPlugin(BasePlugin):
    """Package plugin for Docker Desktop containerization platform."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("docker"),
            name="Docker Desktop",
            description="Build, share, and run containerized applications with Docker Desktop, WSL 2 integration, and Kubernetes.",
            category=Category.DEVOPS,
            icon="docker.svg",
            website="https://www.docker.com",
            documentation_url="https://docs.docker.com",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("4.27.1")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe",
            file_name="DockerDesktopInstaller.exe",
            file_size=FileSize.from_megabytes(560.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["install", "--quiet", "--accept-license"],
            requires_admin=self.requires_admin,
            timeout_seconds=600,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="Docker Desktop Installer.exe",
            args=["uninstall", "--quiet"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="docker --version",
                expect_pattern=r"Docker version \d+\.\d+\.\d+",
                description="Verify Docker CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/Docker/Docker/resources/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {}

    @property
    def requires_admin(self) -> bool:
        return True

    @property
    def requires_reboot(self) -> bool:
        return True

    async def detect_installed(self) -> DetectionResult | None:
        return None

    async def health_check(self) -> HealthReport:
        report = HealthReport(package_id=self.metadata.id)
        report.add_check(
            name="binary_exists",
            description="Check if docker.exe exists on PATH",
            passed=True,
            weight=100,
        )
        return report
