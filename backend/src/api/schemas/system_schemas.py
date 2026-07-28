"""
Pydantic DTO schemas for system routes.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class GPUInfoResponse(BaseModel):
    vendor: str
    device_name: str
    driver_version: Optional[str] = None
    vram_mb: Optional[int] = None
    cuda_version: Optional[str] = None


class SystemInfoResponse(BaseModel):
    os_name: str
    os_version: str
    os_build: int
    architecture: str
    total_ram_mb: int
    available_disk_gb: float
    gpus: List[GPUInfoResponse]
    cpu_cores: int


class HealthSummaryResponse(BaseModel):
    score: int
    status: str
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    total_installed: int
