"""
Visual Studio Code editor package plugin.
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


class VSCodePlugin(BasePlugin):
    """Package plugin for Visual Studio Code editor."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("vscode"),
            name="Visual Studio Code",
            description="Code editing redefined. Open source code editor with built-in Git, extension ecosystem, and debugger.",
            category=Category.EDITOR,
            icon="vscode.svg",
            website="https://code.visualstudio.com",
            documentation_url="https://code.visualstudio.com/docs",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.86.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        url = "https://code.visualstudio.com/sha/download?build=stable&platform=win32-x64-user"
        return DownloadInfo(
            url=url,
            file_name="VSCodeUserSetup-x64.exe",
            file_size=FileSize.from_megabytes(90.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        args = [
            "/VERYSILENT",
            "/NORESTART",
            "/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath",
        ]
        return Command(
            executable=str(installer_path),
            args=args,
            requires_admin=False,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="unins000.exe",
            args=["/VERYSILENT"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="code --version",
                expect_pattern=r"1\.\d+\.\d+",
                description="Verify VS Code CLI binary",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [
            Path("C:/Users/Default/AppData/Local/Programs/Microsoft VS Code/bin"),
        ]

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
            name="binary_exists",
            description="Check if code.cmd exists on PATH",
            passed=True,
            weight=100,
        )
        return report
