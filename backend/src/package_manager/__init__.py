"""Package manager & plugin system."""

from src.package_manager.base_plugin import (
    BasePlugin,
    InstallContext,
    InstallOptions,
    UninstallContext,
)
from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_manager import PluginManager
from src.package_manager.plugin_validator import PluginValidator

__all__ = [
    "BasePlugin",
    "DefaultPluginLoader",
    "InstallContext",
    "InstallOptions",
    "PluginManager",
    "PluginValidator",
    "UninstallContext",
]
