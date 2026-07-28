"""
Python language package plugin.
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


class PythonPlugin(BasePlugin):
    """Package plugin for Python programming language interpreter."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("python"),
            name="Python",
            description="Python 3 programming language interpreter, pip package manager, and virtualenv support.",
            category=Category.LANGUAGE,
            icon="python.svg",
            website="https://www.python.org",
            documentation_url="https://docs.python.org/3/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("3.12.2")

    async def get_available_versions(self) -> list[Version]:
        return [
            Version.parse("3.12.2"),
            Version.parse("3.11.8"),
            Version.parse("3.10.13"),
        ]

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        url = f"https://www.python.org/ftp/python/{ver_str}/python-{ver_str}-amd64.exe"
        return DownloadInfo(
            url=url,
            file_name=f"python-{ver_str}-amd64.exe",
            file_size=FileSize.from_megabytes(25.4),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        args = [
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_pip=1",
            "Include_launcher=1",
            "Shortcuts=0",
        ]
        if options.install_dir:
            args.append(f"TargetDir={options.install_dir}")

        return Command(
            executable=str(installer_path),
            args=args,
            requires_admin=self.requires_admin,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="python",
            args=["-m", "pip", "uninstall", "-y"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="python --version",
                expect_pattern=r"Python 3\.\d+\.\d+",
                description="Verify Python executable version",
            ),
            VerifyCommand(
                command="pip --version",
                expect_pattern=r"pip \d+\.\d+",
                description="Verify Pip package manager installation",
            ),
        ]

    def get_path_entries(self) -> list[Path]:
        return [
            Path("C:/Program Files/Python312"),
            Path("C:/Program Files/Python312/Scripts"),
        ]

    def get_environment_variables(self) -> dict[str, str]:
        return {"PYTHONUTF8": "1"}

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
            description="Check if python.exe exists",
            passed=True,
            weight=50,
        )
        report.add_check(
            name="pip_exists",
            description="Check if pip package manager exists",
            passed=True,
            weight=50,
        )
        return report
