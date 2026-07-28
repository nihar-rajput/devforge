"""
Precision test suite validating all 36 package plugins.
"""

import pytest
from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_manager import PluginManager
from src.package_manager.plugin_validator import PluginValidator
from src.core.enums import Category, InstallerType
from src.core.value_objects.version import Version


@pytest.mark.asyncio
async def test_all_36_plugins_catalog_precision():
    """Verify all 36 plugins adhere to BasePlugin contract and pass validator."""
    loader = DefaultPluginLoader()
    plugins = await loader.load_all_plugins()

    assert len(plugins) == 36, f"Expected 36 registered plugins, found {len(plugins)}"

    for pkg_id, plugin in plugins.items():
        # Validate class structure
        PluginValidator.validate(type(plugin))

        # Check metadata
        meta = plugin.metadata
        assert str(meta.id) == pkg_id
        assert len(meta.name) > 0
        assert len(meta.description) > 0
        assert isinstance(meta.category, Category)

        # Check version resolution
        ver = await plugin.get_latest_version()
        assert isinstance(ver, Version)
        assert len(str(ver)) > 0

        # Check download info
        dl = await plugin.get_download_info(ver)
        assert dl.url.startswith("http://") or dl.url.startswith("https://")
        assert len(dl.file_name) > 0
        assert isinstance(dl.installer_type, InstallerType)
        assert dl.file_size.bytes_count > 0

        # Check verify commands
        v_cmds = plugin.get_verify_commands()
        assert len(v_cmds) >= 1
        for vc in v_cmds:
            assert len(vc.command) > 0
            assert len(vc.expect_pattern) > 0
