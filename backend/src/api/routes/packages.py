"""
Packages REST API endpoints.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_package_service
from src.api.schemas.package_schemas import PackageDetailResponse, PackageResponse
from src.core.enums import Category
from src.core.value_objects.package_id import PackageId
from src.services.package_service import PackageService

router = APIRouter(prefix="/packages", tags=["Packages"])


@router.get("", response_model=List[PackageResponse])
async def list_packages(
    category: Optional[Category] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query string"),
    package_service: PackageService = Depends(get_package_service),
) -> List[PackageResponse]:
    """List or search all software packages in the DevForge catalog."""
    if search:
        packages = await package_service.search_packages(search)
    elif category:
        packages = await package_service.get_packages_by_category(category)
    else:
        packages = await package_service.get_all_packages()

    return [
        PackageResponse(
            id=p.id.value,
            name=p.metadata.name,
            description=p.metadata.description,
            category=p.metadata.category.value,
            icon=p.metadata.icon,
            website=p.metadata.website,
            status=p.status.value,
            installed_version=str(p.installed_version) if p.installed_version else None,
            latest_version=str(p.latest_version) if p.latest_version else None,
            health_score=p.health_score,
            has_update=p.has_update,
            is_installed=p.is_installed,
        )
        for p in packages
    ]


@router.get("/{package_id}", response_model=PackageDetailResponse)
async def get_package(
    package_id: str,
    package_service: PackageService = Depends(get_package_service),
) -> PackageDetailResponse:
    """Get detailed metadata for a specific package by ID."""
    pkg_id = PackageId.of(package_id)
    package = await package_service.get_package_by_id(pkg_id)

    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package '{package_id}' not found in catalog.",
        )

    return PackageDetailResponse(
        id=package.id.value,
        name=package.metadata.name,
        description=package.metadata.description,
        category=package.metadata.category.value,
        icon=package.metadata.icon,
        website=package.metadata.website,
        status=package.status.value,
        installed_version=str(package.installed_version) if package.installed_version else None,
        latest_version=str(package.latest_version) if package.latest_version else None,
        health_score=package.health_score,
        has_update=package.has_update,
        is_installed=package.is_installed,
        install_path=str(package.install_path) if package.install_path else None,
        dependencies=[d.package_id.value for d in package.dependencies],
        documentation_url=package.metadata.documentation_url,
    )
