"""
Unit tests for DependencyResolver, DependencyGraph, and VersionConstraint.
"""

from __future__ import annotations

import pytest

from src.core.entities.package import Dependency, DownloadInfo, PluginMetadata
from src.core.entities.health_report import HealthReport
from src.core.enums import Category, InstallerType
from src.core.errors.dependency_errors import CircularDependencyError
from src.core.ports.process_runner import Command, VerifyCommand
from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.checksum import Checksum
from src.core.value_objects.file_size import FileSize
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.dependency_resolver.constraint import VersionConstraint
from src.dependency_resolver.resolver import DependencyResolver
from src.package_manager.base_plugin import BasePlugin, InstallOptions
from src.package_manager.plugin_manager import PluginManager


class PkgAPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(id=PackageId.of("pkg-a"), name="A", description="A", category=Category.UTILITY)
    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(package_id=PackageId.of("pkg-b"))]
    async def get_latest_version(self) -> Version: return Version.parse("1.0.0")
    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(url="http://ex.com/a.exe", file_name="a.exe")
    def get_install_command(self, path, opts) -> Command: return Command(executable="a.exe")
    def get_uninstall_command(self) -> Command: return Command(executable="un-a.exe")
    def get_verify_commands(self) -> list[VerifyCommand]: return []
    def get_path_entries(self) -> list: return []
    def get_environment_variables(self) -> dict: return {}
    @property
    def requires_admin(self) -> bool: return False
    @property
    def requires_reboot(self) -> bool: return False
    async def detect_installed(self): return None
    async def health_check(self): return HealthReport(package_id=self.metadata.id)


class PkgBPlugin(BasePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(id=PackageId.of("pkg-b"), name="B", description="B", category=Category.UTILITY)
    @property
    def dependencies(self) -> list[Dependency]: return []
    async def get_latest_version(self) -> Version: return Version.parse("1.0.0")
    async def get_download_info(self, version: Version) -> DownloadInfo:
        return DownloadInfo(url="http://ex.com/b.exe", file_name="b.exe")
    def get_install_command(self, path, opts) -> Command: return Command(executable="b.exe")
    def get_uninstall_command(self) -> Command: return Command(executable="un-b.exe")
    def get_verify_commands(self) -> list[VerifyCommand]: return []
    def get_path_entries(self) -> list: return []
    def get_environment_variables(self) -> dict: return {}
    @property
    def requires_admin(self) -> bool: return False
    @property
    def requires_reboot(self) -> bool: return False
    async def detect_installed(self): return None
    async def health_check(self): return HealthReport(package_id=self.metadata.id)


def test_version_constraint_matching() -> None:
    c = VersionConstraint(">=3.10.0, <4.0.0")
    assert c.is_satisfied_by(Version.parse("3.12.1")) is True
    assert c.is_satisfied_by(Version.parse("2.7.0")) is False

    tilde = VersionConstraint("~=3.12.0")
    assert tilde.is_satisfied_by(Version.parse("3.12.5")) is True
    assert tilde.is_satisfied_by(Version.parse("3.13.0")) is False


def test_dependency_resolver_topological_sort() -> None:
    pm = PluginManager()
    pm.register_plugin(PkgAPlugin())
    pm.register_plugin(PkgBPlugin())

    resolver = DependencyResolver(pm)
    order = resolver.resolve_installation_order([PackageId.of("pkg-a")])

    # pkg-b has no dependencies, pkg-a depends on pkg-b -> pkg-b must come before pkg-a
    assert [p.value for p in order] == ["pkg-b", "pkg-a"]
