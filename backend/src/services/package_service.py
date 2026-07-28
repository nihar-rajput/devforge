"""
Package service implementation.
"""

from __future__ import annotations

from typing import List

from src.core.entities.package import Package
from src.core.enums import Category, PackageStatus
from src.core.ports.package_repository import PackageRepository
from src.core.value_objects.package_id import PackageId
from src.package_manager.plugin_manager import PluginManager


class PackageService:
    """
    High-level application service for package catalog operations.
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        package_repo: PackageRepository | None = None,
    ) -> None:
        self._plugin_manager = plugin_manager
        self._package_repo = package_repo

    async def get_all_packages(self) -> List[Package]:
        """Get all packages available in the DevForge catalog."""
        if self._package_repo:
            db_packages = await self._package_repo.get_all()
            if db_packages:
                return db_packages

        # Fallback to plugins
        plugins = self._plugin_manager.get_all_plugins()
        packages: List[Package] = []
        for plugin in plugins:
            ver = await plugin.get_latest_version()
            pkg = Package(
                id=plugin.metadata.id,
                metadata=plugin.metadata,
                status=PackageStatus.AVAILABLE,
                latest_version=ver,
                dependencies=plugin.dependencies,
            )
            packages.append(pkg)

        return packages

    async def get_package_by_id(self, package_id: PackageId) -> Package | None:
        """Get package details by ID."""
        if self._package_repo:
            pkg = await self._package_repo.get_by_id(package_id)
            if pkg:
                return pkg

        plugin = self._plugin_manager.get_plugin(package_id)
        if not plugin:
            return None

        ver = await plugin.get_latest_version()
        return Package(
            id=plugin.metadata.id,
            metadata=plugin.metadata,
            status=PackageStatus.AVAILABLE,
            latest_version=ver,
            dependencies=plugin.dependencies,
        )

    async def get_packages_by_category(self, category: Category) -> List[Package]:
        """Filter packages by category."""
        all_pkgs = await self.get_all_packages()
        return [p for p in all_pkgs if p.metadata.category == category]

    async def search_packages(self, query: str) -> List[Package]:
        """Search packages by query string."""
        q = query.lower().strip()
        all_pkgs = await self.get_all_packages()
        results: List[Package] = []
        for p in all_pkgs:
            if q in p.id.value.lower() or q in p.metadata.name.lower() or q in p.metadata.description.lower():
                results.append(p)
        return results
