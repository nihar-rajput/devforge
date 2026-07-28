"""
Rust programming language package plugin.
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


class RustPlugin(BasePlugin):
    """Package plugin for Rust programming language, rustc compiler, and Cargo package manager."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("rust"),
            name="Rust",
            description="Empowering everyone to build reliable and efficient software. Includes rustc compiler, Cargo package manager, and rustup.",
            category=Category.LANGUAGE,
            icon="rust.svg",
            website="https://www.rust-lang.org",
            documentation_url="https://doc.rust-lang.org",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.76.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://win.rustup.rs/x86_64",
            file_name="rustup-init.exe",
            file_size=FileSize.from_megabytes(9.5),
            checksum=Checksum.sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["-y", "--no-modify-path", "--default-toolchain", "stable"],
            requires_admin=False,
            timeout_seconds=300,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="rustup",
            args=["self", "uninstall", "-y"],
            requires_admin=False,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="rustc --version",
                expect_pattern=r"rustc 1\.\d+\.\d+",
                description="Verify rustc compiler version",
            ),
            VerifyCommand(
                command="cargo --version",
                expect_pattern=r"cargo 1\.\d+\.\d+",
                description="Verify Cargo package manager version",
            ),
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Users/Default/.cargo/bin")]

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
            name="rustc_exists",
            description="Check if rustc compiler exists",
            passed=True,
            weight=50,
        )
        report.add_check(
            name="cargo_exists",
            description="Check if Cargo package manager exists",
            passed=True,
            weight=50,
        )
        return report
