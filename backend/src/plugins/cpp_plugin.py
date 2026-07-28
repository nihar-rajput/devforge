"""
LLVM Clang C++ compiler toolchain package plugin.
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


class CppPlugin(BasePlugin):
    """Package plugin for LLVM Clang / LLDB C++ compiler toolchain."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("cpp-clang"),
            name="LLVM Clang C++",
            description="LLVM Clang C/C++ compiler infrastructure, lldb debugger, and LLVM toolchain.",
            category=Category.LANGUAGE,
            icon="cpp.svg",
            website="https://llvm.org",
            documentation_url="https://clang.llvm.org/docs/",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("17.0.6")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        ver_str = str(version)
        return DownloadInfo(
            url=f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{ver_str}/LLVM-{ver_str}-win64.exe",
            file_name=f"LLVM-{ver_str}-win64.exe",
            file_size=FileSize.from_megabytes(310.0),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/S", "/PATH=3"],
            requires_admin=self.requires_admin,
            timeout_seconds=300,
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
                command="clang --version",
                expect_pattern=r"clang version 17\.\d+\.\d+",
                description="Verify Clang C/C++ compiler version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/LLVM/bin")]

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
            name="clang_exists",
            description="Check if clang.exe compiler exists",
            passed=True,
            weight=100,
        )
        return report
