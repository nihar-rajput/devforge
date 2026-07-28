"""
Telemetry DTO schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TelemetryPayload(BaseModel):
    app_version: str = Field(default="0.1.0", description="DevForge version")
    timestamp: str = Field(..., description="ISO timestamp of the error event")
    error_type: str = Field(..., description="Exception class or error category")
    package_id: Optional[str] = Field(None, description="Affected package ID if applicable")
    os_info: str = Field(..., description="Operating System version and build")
    error_message: str = Field(..., description="User-facing error message")
    log_snippet: Optional[str] = Field(None, description="Anonymized log output snippet")
    user_consent: bool = Field(default=True, description="Explicit user consent confirmation")


class TelemetrySettings(BaseModel):
    enabled: bool = Field(default=False, description="Whether telemetry reporting is enabled")
    always_ask: bool = Field(default=True, description="Whether to prompt user before sending each report")
    webhook_url: Optional[str] = Field(None, description="Custom error reporting webhook URL")


class TelemetryReportResponse(BaseModel):
    success: bool
    message: str
    report_id: str
