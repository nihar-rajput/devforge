"""
Structured HTTP request logger middleware.
"""

from __future__ import annotations

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("api.http")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware logging every HTTP request and response with latency.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        path = request.url.path
        method = request.method

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            logger.info(
                f"{method} {path} - {response.status_code} ({duration_ms}ms)",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            return response
        except Exception as exc:
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            logger.error(
                f"{method} {path} - FAILED ({duration_ms}ms): {exc}",
                duration_ms=duration_ms,
            )
            raise
