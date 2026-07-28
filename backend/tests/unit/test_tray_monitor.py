"""
Unit tests for TrayMonitorService.
"""

import pytest
from src.package_manager.plugin_manager import PluginManager
from src.plugins.python_plugin import PythonPlugin
from src.services.tray_monitor_service import TrayMonitorService


@pytest.mark.asyncio
async def test_tray_monitor_health_audit():
    pm = PluginManager()
    pm.register_plugin(PythonPlugin())

    monitor = TrayMonitorService(plugin_manager=pm, interval_seconds=10)
    res = await monitor.run_health_audit()

    assert "timestamp" in res
    assert "total_packages" in res
    assert res["total_packages"] >= 1
    assert "healthy_count" in res


@pytest.mark.asyncio
async def test_tray_monitor_start_stop():
    pm = PluginManager()
    monitor = TrayMonitorService(plugin_manager=pm, interval_seconds=1)

    await monitor.start()
    status = monitor.get_status()
    assert status["is_running"] is True

    await monitor.stop()
    status = monitor.get_status()
    assert status["is_running"] is False
