"""
Pydantic DTO schemas for package routes.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class PackageResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    icon: Optional[str] = None
    website: Optional[str] = None
    status: str
    installed_version: Optional[str] = None
    latest_version: Optional[str] = None
    health_score: int
    has_update: bool
    is_installed: bool


class PackageDetailResponse(PackageResponse):
    install_path: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    documentation_url: Optional[str] = None
