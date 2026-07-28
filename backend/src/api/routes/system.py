"""
System REST API endpoints.
"""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, Depends

from src.api.dependencies import get_health_service, get_plugin_manager
from src.api.schemas.system_schemas import GPUInfoResponse, HealthSummaryResponse, SystemInfoResponse
from src.detector.software_detector import DefaultSoftwareDetector
from src.services.health_service import HealthService
from src.services.tray_monitor_service import TrayMonitorService
from src.package_manager.plugin_manager import PluginManager

router = APIRouter(prefix="/system", tags=["System"])

_detector = DefaultSoftwareDetector()
_tray_monitor: TrayMonitorService | None = None


def get_tray_monitor(plugin_mgr: PluginManager = Depends(get_plugin_manager)) -> TrayMonitorService:
    global _tray_monitor
    if _tray_monitor is None:
        _tray_monitor = TrayMonitorService(plugin_manager=plugin_mgr)
    return _tray_monitor


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info() -> SystemInfoResponse:
    """Get system hardware, OS, CPU, RAM, disk, and GPU information."""
    info = await _detector.get_system_info()
    return SystemInfoResponse(
        os_name=info.os_name,
        os_version=info.os_version,
        os_build=info.os_build,
        architecture=info.architecture.value,
        total_ram_mb=info.total_ram_mb,
        available_disk_gb=info.available_disk_gb,
        gpus=[
            GPUInfoResponse(
                vendor=g.vendor.value,
                device_name=g.device_name,
                driver_version=g.driver_version,
                vram_mb=g.vram_mb,
                cuda_version=g.cuda_version,
            )
            for g in info.gpus
        ],
        cpu_cores=info.cpu_cores,
    )


@router.get("/health", response_model=HealthSummaryResponse)
async def get_health_summary(
    health_service: HealthService = Depends(get_health_service),
) -> HealthSummaryResponse:
    """Get aggregate environment health summary score (0-100)."""
    res = await health_service.get_system_health_score()
    return HealthSummaryResponse(
        score=res["score"],
        status=res["status"],
        healthy_count=res["healthy_count"],
        degraded_count=res["degraded_count"],
        unhealthy_count=res["unhealthy_count"],
        total_installed=res["total_installed"],
    )


@router.get("/monitor/status")
async def get_monitor_status(
    monitor: TrayMonitorService = Depends(get_tray_monitor),
) -> Dict[str, Any]:
    """Get status of background health monitor worker."""
    return monitor.get_status()


@router.post("/monitor/trigger")
async def trigger_health_audit(
    monitor: TrayMonitorService = Depends(get_tray_monitor),
) -> Dict[str, Any]:
    """Trigger an immediate background health audit."""
    return await monitor.run_health_audit()
