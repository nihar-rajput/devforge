"""
DevForge Plugin Generator CLI script.

Scaffolds a new package plugin file in src/plugins/ with boilerplate code.

Usage:
    python scripts/create_plugin.py my-tool --name "My Tool" --category language
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TEMPLATE = '''"""
{name} package plugin for DevForge.
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


class {class_name}Plugin(BasePlugin):
    """Package plugin for {name}."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id=PackageId.of("{pkg_id}"),
            name="{name}",
            description="{description}",
            category=Category.{category},
            icon="{pkg_id}.svg",
            website="{website}",
        )

    @property
    def dependencies(self) -> list[Dependency]:
        return []

    async def get_latest_version(self) -> Version:
        return Version.parse("1.0.0")

    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(
            url="https://example.com/download/{pkg_id}-installer.exe",
            file_name="{pkg_id}-installer.exe",
            file_size=FileSize.from_megabytes(10.0),
            checksum=Checksum.sha256("0000000000000000000000000000000000000000000000000000000000000000"),
            installer_type=InstallerType.EXE,
        )

    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        return Command(
            executable=str(installer_path),
            args=["/VERYSILENT", "/NORESTART"],
            requires_admin=self.requires_admin,
        )

    def get_uninstall_command(self) -> Command:
        return Command(
            executable="{pkg_id}-uninstall.exe",
            args=["/VERYSILENT"],
            requires_admin=self.requires_admin,
        )

    def get_verify_commands(self) -> list[VerifyCommand]:
        return [
            VerifyCommand(
                command="{pkg_id} --version",
                expect_pattern=r"1\.\d+\.\d+",
                description="Verify CLI version",
            )
        ]

    def get_path_entries(self) -> list[Path]:
        return [Path("C:/Program Files/{name}/bin")]

    def get_environment_variables(self) -> dict[str, str]:
        return {{}}

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
            description="Check if binary exists",
            passed=True,
            weight=100,
        )
        return report
'''


def to_pascal_case(s: str) -> str:
    """Convert hyphenated string to PascalCase."""
    return "".join(word.capitalize() for word in s.replace("-", "_").split("_"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new DevForge package plugin.")
    parser.add_argument("id", help="Package ID (e.g. 'my-tool')")
    parser.add_argument("--name", help="Human-readable package name", default=None)
    parser.add_argument(
        "--category",
        choices=["language", "editor", "database", "devops", "ai", "utility", "runtime", "version_control"],
        default="utility",
        help="Package category",
    )
    parser.add_argument("--description", help="Package description", default="A software tool for developers.")
    parser.add_argument("--website", help="Package website", default="https://example.com")

    args = parser.parse_args()

    pkg_id = args.id.lower().strip()
    name = args.name or to_pascal_case(pkg_id)
    class_name = to_pascal_case(pkg_id)
    category = args.category.upper()

    script_dir = Path(__file__).resolve().parent
    plugins_dir = script_dir.parent / "src" / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)

    target_file = plugins_dir / f"{pkg_id.replace('-', '_')}_plugin.py"

    if target_file.exists():
        print(f"Error: Plugin file '{target_file}' already exists.", file=sys.stderr)
        sys.exit(1)

    code = TEMPLATE.format(
        pkg_id=pkg_id,
        name=name,
        class_name=class_name,
        category=category,
        description=args.description,
        website=args.website,
    )

    target_file.write_text(code, encoding="utf-8")
    print(f"Successfully generated plugin scaffolding at: {target_file}")


if __name__ == "__main__":
    main()
