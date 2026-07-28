"""
Telemetry REST API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas.telemetry_schemas import TelemetryPayload, TelemetrySettings, TelemetryReportResponse
from src.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

# Global singleton telemetry service
_telemetry_service = TelemetryService()


def get_telemetry_service() -> TelemetryService:
    return _telemetry_service


@router.post("/report", response_model=TelemetryReportResponse, status_code=status.HTTP_200_OK)
async def submit_error_report(
    payload: TelemetryPayload,
    service: TelemetryService = Depends(get_telemetry_service),
) -> TelemetryReportResponse:
    """Submit an error diagnostic report after explicit user consent."""
    return await service.send_report(payload)


@router.get("/settings", response_model=TelemetrySettings)
async def get_telemetry_settings(
    service: TelemetryService = Depends(get_telemetry_service),
) -> TelemetrySettings:
    """Retrieve user telemetry preferences."""
    return service.get_settings()


@router.post("/settings", response_model=TelemetrySettings)
async def update_telemetry_settings(
    settings: TelemetrySettings,
    service: TelemetryService = Depends(get_telemetry_service),
) -> TelemetrySettings:
    """Update user telemetry preferences."""
    return service.update_settings(settings)
