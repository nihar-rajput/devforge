"""
Unit tests for PluginManager, DefaultPluginLoader, and PluginValidator.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.enums import Category
from src.core.value_objects.package_id import PackageId
from src.package_manager.base_plugin import BasePlugin
from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_manager import PluginManager
from src.package_manager.plugin_validator import PluginValidator, PluginValidationError
from src.plugins.python_plugin import PythonPlugin


def test_plugin_validator_valid() -> None:
    assert PluginValidator.validate(PythonPlugin) is True


def test_plugin_validator_invalid_class() -> None:
    with pytest.raises(PluginValidationError):
        PluginValidator.validate(dict)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_plugin_manager_registration_and_lookup() -> None:
    manager = PluginManager()
    python_plugin = PythonPlugin()

    manager.register_plugin(python_plugin)

    assert manager.count == 1
    retrieved = manager.get_plugin(PackageId.of("python"))
    assert retrieved is not None
    assert retrieved.metadata.name == "Python"

    # Search
    search_results = manager.search_plugins("python")
    assert len(search_results) == 1

    # Category filter
    lang_plugins = manager.get_plugins_by_category(Category.LANGUAGE)
    assert len(lang_plugins) == 1


@pytest.mark.asyncio
async def test_default_plugin_loader_discovery() -> None:
    plugins_dir = Path(__file__).resolve().parents[2] / "src" / "plugins"
    loader = DefaultPluginLoader(plugin_dir=plugins_dir)

    plugins = await loader.load_all_plugins()
    assert "python" in plugins
    assert "git" in plugins
    assert "vscode" in plugins
    assert "nodejs" in plugins
