"""
Installations REST API endpoints.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_installation_service
from src.api.schemas.install_schemas import InstallationResponse, InstallRequest
from src.core.value_objects.package_id import PackageId
from src.package_manager.base_plugin import InstallOptions
from src.services.installation_service import InstallationService

router = APIRouter(prefix="", tags=["Installations"])


@router.post("/install", response_model=List[InstallationResponse], status_code=status.HTTP_202_ACCEPTED)
async def install_packages(
    request: InstallRequest,
    service: InstallationService = Depends(get_installation_service),
) -> List[InstallationResponse]:
    """Start installation of a list of packages and their dependencies."""
    pkg_ids = [PackageId.of(p) for p in request.packages]
    options = InstallOptions(
        all_users=request.all_users,
        add_to_path=request.add_to_path,
    )

    installations = await service.install_stack(pkg_ids, options)

    return [
        InstallationResponse(
            id=str(inst.id),
            package_id=inst.package_id.value,
            target_version=str(inst.target_version),
            current_stage=inst.current_stage.value,
            progress_percent=inst.progress_percent,
            is_cancelled=inst.is_cancelled,
            error_summary=inst.error_summary,
        )
        for inst in installations
    ]


@router.post("/uninstall/{package_id}", status_code=status.HTTP_200_OK)
async def uninstall_package(
    package_id: str,
    service: InstallationService = Depends(get_installation_service),
) -> dict:
    """Uninstall a package cleanly."""
    pkg_id = PackageId.of(package_id)
    success = await service.uninstall_package(pkg_id)
    return {"package_id": package_id, "success": success}


@router.post("/repair/{package_id}", status_code=status.HTTP_200_OK)
async def repair_package(
    package_id: str,
    service: InstallationService = Depends(get_installation_service),
) -> dict:
    """Trigger automated repair for a broken package."""
    pkg_id = PackageId.of(package_id)
    success = await service.repair_package(pkg_id)
    return {"package_id": package_id, "repaired": success}
