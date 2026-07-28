"""
Pydantic DTO schemas for installation routes.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class InstallRequest(BaseModel):
    packages: List[str] = Field(..., min_length=1, description="List of package IDs to install.")
    add_to_path: bool = Field(default=True, description="Add package binaries to PATH.")
    all_users: bool = Field(default=True, description="Install for all users if admin.")


class InstallationResponse(BaseModel):
    id: str
    package_id: str
    target_version: str
    current_stage: str
    progress_percent: float
    is_cancelled: bool
    error_summary: Optional[str] = None
