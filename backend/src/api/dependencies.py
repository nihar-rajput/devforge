"""
FastAPI dependency injection wiring.
"""

from __future__ import annotations

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.sqlite_package_repo import SqlitePackageRepository
from src.database.session import get_db_session
from src.downloader.manager import DefaultDownloadManager
from src.events.event_bus import DefaultEventBus
from src.installer.engine import InstallationEngine
from src.installer.step_runner import StepRunner
from src.installer.uninstaller import Uninstaller
from src.package_manager.plugin_manager import PluginManager
from src.repairer.repair_engine import RepairEngine
from src.services.environment_service import EnvironmentService
from src.services.health_service import HealthService
from src.services.installation_service import InstallationService
from src.services.package_service import PackageService
from src.system.path_manager import WindowsPathManager
from src.system.process_runner import AsyncProcessRunner

# Global singletons for in-process components
_event_bus = DefaultEventBus()
_plugin_manager = PluginManager()
_download_manager = DefaultDownloadManager(event_bus=_event_bus)


async def get_plugin_manager() -> PluginManager:
    """Dependency provider for global PluginManager singleton."""
    if _plugin_manager.count == 0:
        await _plugin_manager.initialize()
    return _plugin_manager


async def get_event_bus() -> DefaultEventBus:
    """Dependency provider for global EventBus singleton."""
    return _event_bus


async def get_package_service(
    session: AsyncSession = Depends(get_db_session),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
) -> PackageService:
    """Dependency provider for PackageService."""
    repo = SqlitePackageRepository(session)
    return PackageService(plugin_mgr, repo)


async def get_installation_service(
    session: AsyncSession = Depends(get_db_session),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
) -> InstallationService:
    """Dependency provider for InstallationService."""
    repo = SqlitePackageRepository(session)
    step_runner = StepRunner(downloader=_download_manager, event_bus=_event_bus)
    engine = InstallationEngine(plugin_mgr, package_repo=repo, event_bus=_event_bus, step_runner=step_runner)
    uninstaller = Uninstaller(plugin_mgr, package_repo=repo, event_bus=_event_bus)
    repair = RepairEngine(plugin_mgr, package_repo=repo)
    return InstallationService(plugin_mgr, engine, uninstaller, repair)


async def get_health_service(
    session: AsyncSession = Depends(get_db_session),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
) -> HealthService:
    """Dependency provider for HealthService."""
    repo = SqlitePackageRepository(session)
    return HealthService(plugin_mgr, repo)


async def get_environment_service(
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
) -> EnvironmentService:
    """Dependency provider for EnvironmentService."""
    return EnvironmentService(plugin_mgr)
