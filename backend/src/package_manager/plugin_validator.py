"""
Plugin validation engine.

Verifies that plugin classes strictly adhere to the BasePlugin contract
and provide valid metadata and return types.
"""

from __future__ import annotations

import inspect
from typing import Type

from src.core.errors.base import DevForgeError
from src.package_manager.base_plugin import BasePlugin


class PluginValidationError(DevForgeError):
    """Raised when a plugin fails contract validation."""

    pass


class PluginValidator:
    """
    Validates plugin classes before registration into the PluginManager.
    """

    @classmethod
    def validate(cls, plugin_cls: Type[BasePlugin]) -> bool:
        """
        Validate a plugin class.

        Args:
            plugin_cls: Class inheriting from BasePlugin.

        Returns:
            True if valid.

        Raises:
            PluginValidationError: If the plugin fails validation checks.
        """
        if not inspect.isclass(plugin_cls):
            raise PluginValidationError(
                f"Expected class, got {type(plugin_cls)}",
                details="Plugin must be a Python class.",
            )

        if not issubclass(plugin_cls, BasePlugin):
            raise PluginValidationError(
                f"Class '{plugin_cls.__name__}' must inherit from BasePlugin",
                details="All package plugins must extend BasePlugin ABC.",
            )

        if inspect.isabstract(plugin_cls):
            abstract_methods = getattr(plugin_cls, "__abstractmethods__", set())
            raise PluginValidationError(
                f"Plugin class '{plugin_cls.__name__}' has un-implemented abstract methods",
                details=f"Missing abstract methods: {', '.join(abstract_methods)}",
            )

        # Instantiate to check metadata property
        try:
            instance = plugin_cls()
            metadata = instance.metadata
            if not metadata or not metadata.id or not metadata.name:
                raise PluginValidationError(
                    f"Plugin '{plugin_cls.__name__}' metadata property is incomplete",
                    details="PluginMetadata must contain id and name.",
                )
        except Exception as exc:
            raise PluginValidationError(
                f"Plugin '{plugin_cls.__name__}' instantiation failed during validation",
                cause=exc,
            ) from exc

        return True
