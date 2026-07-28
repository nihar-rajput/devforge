"""
Plugin manager service.

Central service for plugin registration, lookup, search, and lifecycle management.
"""

from __future__ import annotations

from typing import Dict, List

from src.core.enums import Category
from src.core.value_objects.package_id import PackageId
from src.logger.structured_logger import StructuredLogger
from src.package_manager.base_plugin import BasePlugin
from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_validator import PluginValidator

logger = StructuredLogger("package_manager.manager")


class PluginManager:
    """
    Central manager for package plugins.

    Maintains the registry of active plugins, provides lookups by PackageId,
    category filtering, and handles initial discovery and dynamic reloading.
    """

    def __init__(self, loader: DefaultPluginLoader | None = None) -> None:
        self._loader = loader or DefaultPluginLoader()
        self._plugins: Dict[str, BasePlugin] = {}

    async def initialize(self) -> None:
        """Discover and load all package plugins at startup."""
        logger.info("Initializing PluginManager...")
        loaded = await self._loader.load_all_plugins()
        self._plugins = loaded
        logger.info(f"PluginManager initialized with {len(self._plugins)} plugins.")

    def register_plugin(self, plugin: BasePlugin) -> None:
        """
        Manually register a plugin instance.

        Args:
            plugin: Plugin instance implementing BasePlugin.
        """
        PluginValidator.validate(type(plugin))
        pkg_id = plugin.metadata.id.value
        self._plugins[pkg_id] = plugin
        logger.info(f"Registered plugin '{plugin.metadata.name}' ({pkg_id})")

    def get_plugin(self, package_id: PackageId | str) -> BasePlugin | None:
        """
        Get plugin by PackageId or ID string.

        Args:
            package_id: PackageId or raw string ID.

        Returns:
            BasePlugin instance, or None if not registered.
        """
        key = package_id.value if isinstance(package_id, PackageId) else package_id.lower().strip()
        return self._plugins.get(key)

    def get_all_plugins(self) -> List[BasePlugin]:
        """Return list of all registered plugins."""
        return list(self._plugins.values())

    def get_plugins_by_category(self, category: Category) -> List[BasePlugin]:
        """
        Get all plugins belonging to a specific category.

        Args:
            category: Package category enum.

        Returns:
            List of matching plugins.
        """
        return [p for p in self._plugins.values() if p.metadata.category == category]

    def search_plugins(self, query: str) -> List[BasePlugin]:
        """
        Search plugins by name, ID, or description.

        Args:
            query: Search query string.

        Returns:
            List of matching plugins.
        """
        q = query.lower().strip()
        results: List[BasePlugin] = []
        for plugin in self._plugins.values():
            meta = plugin.metadata
            if (
                q in meta.id.value.lower()
                or q in meta.name.lower()
                or q in meta.description.lower()
            ):
                results.append(plugin)
        return results

    async def reload_plugin(self, package_id: PackageId | str) -> BasePlugin:
        """
        Reload a specific plugin from disk.

        Args:
            package_id: PackageId or ID string to reload.

        Returns:
            Reloaded BasePlugin instance.
        """
        key = package_id.value if isinstance(package_id, PackageId) else package_id.lower().strip()
        reloaded = await self._loader.reload_plugin(key)
        self._plugins[key] = reloaded
        return reloaded

    @property
    def count(self) -> int:
        """Number of registered plugins."""
        return len(self._plugins)
