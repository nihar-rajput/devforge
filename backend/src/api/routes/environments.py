"""
Environment Profiles & Snapshot REST API endpoints.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, Body

from src.api.dependencies import get_environment_service
from src.services.environment_service import EnvironmentService

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
