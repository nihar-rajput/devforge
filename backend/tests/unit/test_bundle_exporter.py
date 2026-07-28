"""
Unit tests for BundleExporterService.
"""

import zipfile
import pytest
from src.package_manager.plugin_manager import PluginManager
from src.plugins.python_plugin import PythonPlugin
from src.services.bundle_exporter_service import BundleExporterService


@pytest.mark.asyncio
async def test_bundle_exporter_create_zip():
    plugin_mgr = PluginManager()
    plugin_mgr.register_plugin(PythonPlugin())

    service = BundleExporterService(plugin_manager=plugin_mgr)
    zip_path = await service.create_offline_bundle(
        package_ids=["python"],
        bundle_name="Test_Python_Offline_Bundle",
    )

    assert zip_path.exists()
    assert zip_path.name.endswith(".zip")

    # Verify contents inside created zip file
    with zipfile.ZipFile(zip_path, "r") as z:
        file_list = z.namelist()
        assert "manifest.json" in file_list
        assert "install_offline.bat" in file_list

        manifest_content = z.read("manifest.json").decode("utf-8")
        assert "DevForge Offline Environment Bundle" in manifest_content
        assert "python" in manifest_content

        bat_content = z.read("install_offline.bat").decode("utf-8")
        assert "DevForge Automated Offline Installer" in bat_content
