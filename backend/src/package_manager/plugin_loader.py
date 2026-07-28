"""
Plugin loader implementation.

Scans plugin directories and entry points, dynamically importing modules
and loading plugin classes.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Type

from src.config.settings import AppSettings
from src.core.errors.base import DevForgeError
from src.core.ports.plugin_loader import PluginLoader
from src.logger.structured_logger import StructuredLogger
from src.package_manager.base_plugin import BasePlugin
from src.package_manager.plugin_validator import PluginValidator

logger = StructuredLogger("package_manager.loader")


class PluginLoadError(DevForgeError):
    """Raised when a plugin fails to load or import."""

    pass


class DefaultPluginLoader(PluginLoader):
    """
    Default implementation of PluginLoader.

    Scans the configured plugin directory (`src/plugins`), imports modules,
    finds valid `BasePlugin` implementations, and instantiates them.
    """

    def __init__(self, plugin_dir: Path | None = None) -> None:
        settings = AppSettings()
        self._plugin_dir = plugin_dir or settings.paths.plugin_dir

    async def discover_plugins(self) -> List[str]:
        """Discover all python files in the plugins directory."""
        if not self._plugin_dir.exists():
            logger.warning(f"Plugin directory '{self._plugin_dir}' does not exist.")
            return []

        plugin_files: List[str] = []
        for file in self._plugin_dir.glob("*.py"):
            if file.name.startswith("_") or file.name.startswith("."):
                continue
            plugin_files.append(str(file))

        return plugin_files

    async def load_plugin(self, plugin_path: str) -> BasePlugin:
        """
        Load a plugin from a file path or module dot-path.

        Args:
            plugin_path: Path to .py file or python module name.

        Returns:
            Instantiated BasePlugin instance.
        """
        path = Path(plugin_path)
        if path.exists() and path.suffix == ".py":
            module_name = f"devforge.plugins.{path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if not spec or not spec.loader:
                raise PluginLoadError(f"Cannot load module spec from '{plugin_path}'")
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as exc:
                raise PluginLoadError(f"Failed to execute plugin module '{plugin_path}'", cause=exc) from exc
        else:
            try:
                module = importlib.import_module(plugin_path)
            except Exception as exc:
                raise PluginLoadError(f"Failed to import plugin module '{plugin_path}'", cause=exc) from exc

        # Find BasePlugin subclass in module
        plugin_cls: Type[BasePlugin] | None = None
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                plugin_cls = obj
                break

        if not plugin_cls:
            raise PluginLoadError(f"No BasePlugin implementation found in module '{plugin_path}'")

        # Validate plugin class contract
        PluginValidator.validate(plugin_cls)

        # Instantiate
        try:
            return plugin_cls()
        except Exception as exc:
            raise PluginLoadError(f"Failed to instantiate plugin class '{plugin_cls.__name__}'", cause=exc) from exc

    async def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Discover and load all valid plugins.

        Returns:
            Dict mapping package ID strings to BasePlugin instances.
        """
        discovered = await self.discover_plugins()
        loaded_plugins: Dict[str, BasePlugin] = {}

        for file_path in discovered:
            try:
                plugin = await self.load_plugin(file_path)
                pkg_id = plugin.metadata.id.value
                loaded_plugins[pkg_id] = plugin
                logger.info(f"Loaded plugin '{plugin.metadata.name}' ({pkg_id})")
            except Exception as exc:
                logger.error(f"Failed to load plugin from '{file_path}': {exc}")

        return loaded_plugins

    async def reload_plugin(self, plugin_id: str) -> BasePlugin:
        """Reload a specific plugin by scanning the directory for matching package ID."""
        discovered = await self.discover_plugins()
        for file_path in discovered:
            try:
                plugin = await self.load_plugin(file_path)
                if plugin.metadata.id.value == plugin_id:
                    logger.info(f"Reloaded plugin '{plugin_id}'")
                    return plugin
            except Exception:
                continue

        raise PluginLoadError(f"Plugin with ID '{plugin_id}' not found for reload.")
