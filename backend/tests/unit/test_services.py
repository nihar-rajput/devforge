"""
Unit tests for Repairer, Updater, and Application Services.
"""

from __future__ import annotations

import pytest

from src.core.entities.environment import EnvironmentProfile
from src.core.enums import Category
from src.core.value_objects.package_id import PackageId
from src.core.value_objects.version import Version
from src.package_manager.plugin_manager import PluginManager
from src.plugins.python_plugin import PythonPlugin
from src.repairer.repair_engine import RepairEngine
from src.services.environment_service import EnvironmentService
from src.services.health_service import HealthService
from src.services.package_service import PackageService
from src.updater.update_checker import UpdateChecker


@pytest.mark.asyncio
async def test_health_service() -> None:
    pm = PluginManager()
    pm.register_plugin(PythonPlugin())

    hs = HealthService(pm)
    res = await hs.get_system_health_score()

    assert res["score"] >= 0
    assert res["total_installed"] == 1


@pytest.mark.asyncio
async def test_package_service() -> None:
    pm = PluginManager()
    pm.register_plugin(PythonPlugin())

    ps = PackageService(pm)
    all_pkgs = await ps.get_all_packages()
    assert len(all_pkgs) == 1
    assert all_pkgs[0].id == PackageId.of("python")

    lang_pkgs = await ps.get_packages_by_category(Category.LANGUAGE)
    assert len(lang_pkgs) == 1


@pytest.mark.asyncio
async def test_environment_service_snapshot() -> None:
    pm = PluginManager()
    pm.register_plugin(PythonPlugin())

    env_svc = EnvironmentService(pm)
    stacks = env_svc.get_default_stacks()
    assert len(stacks) >= 3

    profile = await env_svc.create_profile_from_installed("My Profile")
    assert profile.name == "My Profile"
    assert profile.package_count == 1

    json_str = env_svc.export_profile_json(profile)
    imported = env_svc.import_profile_json(json_str)
    assert imported.name == "My Profile"
    assert imported.package_count == 1


@pytest.mark.asyncio
async def test_update_checker() -> None:
    pm = PluginManager()
    pm.register_plugin(PythonPlugin())

    checker = UpdateChecker(pm)
    updates = await checker.check_updates()
    assert "python" in updates
