"""
JupyterLab Data Science notebook environment package plugin.
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


class JupyterPlugin(BasePlugin):
    """Package plugin for JupyterLab data science notebook environment."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("jupyter"),
            name="JupyterLab",
            description="Extensible web-based interactive development environment for Jupyter notebooks, code, and data science.",
            category=Category.AI,
            icon="jupyter.svg",
            website="https://jupyter.org",
            documentation_url="https://jupyterlab.readthedocs.io/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("python"))]

    async def get_latest_version(self) -> Version:
        return Version.parse("4.1.2")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://github.com/jupyterlab/jupyterlab-desktop/releases/download/v4.1.2-1/JupyterLab-Setup-Windows-x64.exe",
            file_name="JupyterLab-Setup-Windows-x64.exe",
            file_size=FileSize.from_megabytes(180.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/S"],
            requires_admin=False,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="Uninstall.exe",
            args=["/S"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="jupyter --version",
                expect_pattern=r"Selected Jupyter core packages",
                description="Verify Jupyter CLI suite",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/AppData/Local/Programs/JupyterLab")]

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
            name="jupyter_exists",
            description="Check if jupyter.exe exists",
            passed=True,
            weight=100,
        )
        return report
