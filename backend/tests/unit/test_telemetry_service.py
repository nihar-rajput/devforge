"""
Unit tests for TelemetryService.
"""

import pytest
from src.api.schemas.telemetry_schemas import TelemetryPayload, TelemetrySettings
from src.services.telemetry_service import TelemetryService


@pytest.mark.asyncio
async def test_telemetry_sanitize_log_snippet():
    service = TelemetryService()
    raw_log = "Error in file C:\\Users\\nihar\\AppData\\Local\\DevForge\\cache\\test.exe and /home/nihar/test"
    sanitized = service.sanitize_log_snippet(raw_log)

    assert "nihar" not in sanitized
    assert "C:\\Users\\<User>\\" in sanitized
    assert "/home/<User>/" in sanitized


@pytest.mark.asyncio
async def test_telemetry_report_with_consent():
    service = TelemetryService()
    payload = TelemetryPayload(
        app_version="0.1.0",
        timestamp="2026-07-28T12:00:00Z",
        error_type="TestError",
        package_id="python",
        os_info="Windows 10",
        error_message="Test crash message",
        log_snippet="Traceback: C:\\Users\\john\\app.py",
        user_consent=True,
    )

    res = await service.send_report(payload)
    assert res.success is True
    assert len(res.report_id) > 0


@pytest.mark.asyncio
async def test_telemetry_report_without_consent():
    service = TelemetryService()
    payload = TelemetryPayload(
        app_version="0.1.0",
        timestamp="2026-07-28T12:00:00Z",
        error_type="TestError",
        error_message="Test message",
        os_info="Windows 10",
        user_consent=False,
    )

    res = await service.send_report(payload)
    assert res.success is False
    assert "User consent not granted" in res.message
