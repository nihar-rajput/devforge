"""
Environment Profiles & Snapshot REST API endpoints.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.responses import FileResponse

from src.api.dependencies import get_environment_service, get_plugin_manager
from src.api.schemas.bundle_schemas import ExportBundleRequest
from src.services.bundle_exporter_service import BundleExporterService
from src.services.environment_service import EnvironmentService
from src.package_manager.plugin_manager import PluginManager

router = APIRouter(prefix="/environments", tags=["Environments"])


@router.get("/stacks")
async def get_stacks(
    service: EnvironmentService = Depends(get_environment_service),
) -> list:
    """Get predefined development stack templates for welcome screen."""
    return service.get_default_stacks()


@router.post("/snapshot")
async def create_snapshot(
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True),
    service: EnvironmentService = Depends(get_environment_service),
) -> dict:
    """Create an environment snapshot profile from currently installed software."""
    profile = await service.create_profile_from_installed(name, description)
    return {"id": str(profile.id), "name": profile.name, "packages": [p.package_id.value for p in profile.packages]}


@router.post("/export")
async def export_profile(
    profile_id: str = Body(..., embed=True),
    service: EnvironmentService = Depends(get_environment_service),
) -> dict:
    """Export profile as JSON string manifest."""
    profiles = service.get_profiles()
    for p in profiles:
        if str(p.id) == profile_id:
            json_manifest = service.export_profile_json(p)
            return {"manifest": json_manifest}

    return {"error": "Profile not found"}


@router.post("/export-bundle")
async def export_offline_bundle(
    request: ExportBundleRequest,
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
) -> FileResponse:
    """Dynamically build and stream a downloadable .zip offline installer bundle for selected packages."""
    if not request.packages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide at least one package ID to export offline bundle.",
        )

    exporter = BundleExporterService(plugin_manager=plugin_mgr)
    try:
        zip_path = await exporter.create_offline_bundle(
            package_ids=request.packages,
            bundle_name=request.bundle_name,
        )
        return FileResponse(
            path=str(zip_path),
            filename=zip_path.name,
            media_type="application/zip",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create offline bundle: {str(e)}",
        )
