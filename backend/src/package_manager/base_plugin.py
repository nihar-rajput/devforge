"""
Abstract plugin contract for package plugins.

Every software package managed by DevForge is represented by a class
inheriting from BasePlugin.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from src.core.entities.package import Dependency, DownloadInfo, PluginMetadata
from src.core.entities.health_report import HealthReport
from src.core.ports.process_runner import Command, VerifyCommand
from src.core.ports.system_detector import DetectionResult
from src.core.value_objects.version import Version


class InstallOptions:
    """Options passed to plugin installation hooks."""

    def __init__(
        self,
        install_dir: Path | None = None,
        all_users: bool = True,
        add_to_path: bool = True,
        custom_args: list[str] | None = None,
    ) -> None:
        self.install_dir = install_dir
        self.all_users = all_users
        self.add_to_path = add_to_path
        self.custom_args = custom_args or []


class InstallContext:
    """Context information passed during installation execution."""

    def __init__(
        self,
        installer_path: Path,
        version: Version,
        options: InstallOptions,
    ) -> None:
        self.installer_path = installer_path
        self.version = version
        self.options = options


class UninstallContext:
    """Context information passed during uninstallation execution."""

    def __init__(self, install_path: Path | None = None) -> None:
        self.install_path = install_path


class BasePlugin(ABC):
    """
    Contract that every package plugin must implement.

    Adding a new package to DevForge requires only creating a new class
    inheriting from BasePlugin and implementing its abstract methods.
    Zero modification to the core installation engine is required.
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Package identity: ID, name, description, category, icon."""

    @property
    @abstractmethod
    def dependencies(self) -> list[Dependency]:
        """List of dependencies required by this package."""

    @abstractmethod
    async def get_latest_version(self) -> Version:
        """Fetch the latest available version from vendor API or website."""

    async def get_available_versions(self) -> list[Version]:
        """Return list of selectable versions available for installation (latest first)."""
        latest = await self.get_latest_version()
        return [latest]

    @abstractmethod
    async def get_download_info(self, version: Version) -> DownloadInfo:
        """Return download URL, expected checksum, file size for a version."""

    @abstractmethod
    def get_install_command(self, installer_path: Path, options: InstallOptions) -> Command:
        """Return the silent install command to execute."""

    @abstractmethod
    def get_uninstall_command(self) -> Command:
        """Return the silent uninstall command to execute."""

    @abstractmethod
    def get_verify_commands(self) -> list[VerifyCommand]:
        """Return commands to verify successful installation."""

    @abstractmethod
    def get_path_entries(self) -> list[Path]:
        """Return directories that must be added to system/user PATH."""

    @abstractmethod
    def get_environment_variables(self) -> dict[str, str]:
        """Return additional environment variables to set (e.g. JAVA_HOME)."""

    @property
    @abstractmethod
    def requires_admin(self) -> bool:
        """Whether this installation requires administrator privileges."""

    @property
    @abstractmethod
    def requires_reboot(self) -> bool:
        """Whether a system reboot is required after installation."""

    @abstractmethod
    async def detect_installed(self) -> DetectionResult | None:
        """Detect if this package is already installed on the host system."""

    @abstractmethod
    async def health_check(self) -> HealthReport:
        """Run a comprehensive health assessment on the package installation."""

    # Optional lifecycle hooks with default empty implementations
    async def pre_install(self, context: InstallContext) -> None:
        """Hook called before download/install begins."""
        pass

    async def post_install(self, context: InstallContext) -> None:
        """Hook called after silent install & verification finish."""
        pass

    async def pre_uninstall(self, context: UninstallContext) -> None:
        """Hook called before uninstallation begins."""
        pass

    async def post_uninstall(self, context: UninstallContext) -> None:
        """Hook called after uninstallation finishes."""
        pass
