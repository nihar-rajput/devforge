"""
Plugin loader port.

Abstract interface for discovering and loading package plugins
at runtime via directory scanning or entry points.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.value_objects.package_id import PackageId


class PluginLoader(ABC):
    """
    Abstract interface for plugin discovery and loading.

    Implementations scan directories or entry points for classes
    that implement the BasePlugin contract, validate them, and
    return instantiated plugin objects.
    """

    @abstractmethod
    async def discover_plugins(self) -> list[str]:
        """
        Discover all available plugin identifiers.

        Returns:
            List of plugin module paths or entry point names.
        """

    @abstractmethod
    async def load_plugin(self, plugin_path: str) -> object:
        """
        Load and instantiate a single plugin.

        Args:
            plugin_path: Module path or entry point name.

        Returns:
            Instantiated plugin object implementing BasePlugin.

        Raises:
            PluginLoadError: If the plugin cannot be loaded or fails validation.
        """

    @abstractmethod
    async def load_all_plugins(self) -> dict[str, object]:
        """
        Discover and load all available plugins.

        Returns:
            Dict mapping package ID strings to plugin instances.
        """

    @abstractmethod
    async def reload_plugin(self, plugin_id: str) -> object:
        """
        Reload a specific plugin (for hot-reload during development).

        Args:
            plugin_id: Package ID of the plugin to reload.

        Returns:
            Reloaded plugin instance.
        """
