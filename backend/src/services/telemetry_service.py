"""
Telemetry Service implementation.
"""

from __future__ import annotations

import re
import uuid
import urllib.request
import urllib.parse
import json
from typing import Dict, Any

from src.api.schemas.telemetry_schemas import TelemetryPayload, TelemetrySettings, TelemetryReportResponse
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("services.telemetry")


class TelemetryService:
    """Service handling error reporting with privacy scrubbing and user consent."""

    def __init__(self, settings: TelemetrySettings | None = None) -> None:
        self._settings = settings or TelemetrySettings()

    def sanitize_log_snippet(self, text: str) -> str:
        """Sanitize sensitive local paths and username strings from logs."""
        if not text:
            return ""
        # Scrub C:\Users\<Username>\ paths to C:\Users\<Scrubbed>\
        scrubbed = re.sub(r"([C-Z]:\\Users\\)[^\\]+", r"\1<User>", text, flags=re.IGNORECASE)
        # Scrub user home directories
        scrubbed = re.sub(r"(/home/)[^/]+", r"\1<User>", scrubbed)
        return scrubbed

    async def send_report(self, payload: TelemetryPayload) -> TelemetryReportResponse:
        """Send anonymized error report after user consent."""
        report_id = str(uuid.uuid4())[:8]

        if not payload.user_consent:
            logger.warning(f"Telemetry report {report_id} rejected: User consent not granted.")
            return TelemetryReportResponse(
                success=False,
                message="User consent not granted. Report discarded.",
                report_id=report_id,
            )

        # Sanitize log snippet
        sanitized_snippet = self.sanitize_log_snippet(payload.log_snippet or "")
        data: Dict[str, Any] = {
            "report_id": report_id,
            "app_version": payload.app_version,
            "timestamp": payload.timestamp,
            "error_type": payload.error_type,
            "package_id": payload.package_id,
            "os_info": payload.os_info,
            "error_message": payload.error_message,
            "log_snippet": sanitized_snippet,
        }

        logger.info(f"Telemetry report {report_id} generated for error '{payload.error_type}' ({payload.package_id}).")

        # If a custom webhook URL is configured, POST the report
        if self._settings.webhook_url:
            try:
                req = urllib.request.Request(
                    self._settings.webhook_url,
                    data=json.dumps(data).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "DevForge-Telemetry/0.1.0"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    logger.info(f"Telemetry report {report_id} delivered to webhook: HTTP {resp.status}")
            except Exception as e:
                logger.error(f"Failed to post telemetry report {report_id} to webhook: {e}")

        return TelemetryReportResponse(
            success=True,
            message=f"Diagnostic error report {report_id} processed successfully.",
            report_id=report_id,
        )

    def get_settings(self) -> TelemetrySettings:
        return self._settings

    def update_settings(self, new_settings: TelemetrySettings) -> TelemetrySettings:
        self._settings = new_settings
        logger.info(f"Updated telemetry settings: enabled={new_settings.enabled}, always_ask={new_settings.always_ask}")
        return self._settings
