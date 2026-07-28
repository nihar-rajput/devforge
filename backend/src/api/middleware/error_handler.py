"""
Global error handler middleware for mapping DevForgeError exceptions to HTTP responses.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.errors.base import DevForgeError
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("api.error_handler")


def register_error_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with FastAPI application."""

    @app.exception_handler(DevForgeError)
    async def devforge_error_handler(request: Request, exc: DevForgeError) -> JSONResponse:
        logger.error(f"Domain error handling request {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception handling request {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected system error occurred.",
                "details": str(exc),
            },
        )
