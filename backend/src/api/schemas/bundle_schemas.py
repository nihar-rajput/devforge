"""
Bundle Exporter DTO schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExportBundleRequest(BaseModel):
    packages: List[str] = Field(..., description="List of package IDs to bundle for offline install")
    bundle_name: Optional[str] = Field(None, description="Custom name for the offline bundle archive")
    include_devforge_engine: bool = Field(default=True, description="Whether to include portable DevForge launcher")
