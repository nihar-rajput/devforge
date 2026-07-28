"""
DevForge FastAPI application entrypoint.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import get_event_bus, get_plugin_manager
from src.api.middleware.error_handler import register_error_handlers
from src.api.middleware.request_logger import RequestLoggerMiddleware
from src.api.routes import environments, installations, packages, system
from src.api.websocket.connection_manager import WebSocketConnectionManager
from src.config.constants import API_V1_PREFIX, APP_NAME, APP_VERSION
from src.config.logging_config import configure_logging
from src.config.settings import AppSettings
from src.database.session import close_db, init_db
from src.events.event_handlers import persist_event_handler
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("main")
ws_manager = WebSocketConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle event handler."""
    settings = AppSettings()
    configure_logging(log_level=settings.log_level, json_output=not settings.debug)

    logger.info(f"Starting {APP_NAME} v{APP_VERSION} backend server...")

    # Initialize database schema
    await init_db()

    # Initialize plugins & event bus
    plugin_mgr = await get_plugin_manager()
    event_bus = await get_event_bus()

    # Register persistence event handler
    event_bus.subscribe_all(persist_event_handler)

    # Register WebSocket broadcast handler
    async def ws_event_broadcaster(event) -> None:
        await ws_manager.broadcast_json({
            "event_type": event.event_type,
            "message": event.message,
            "payload": event.model_dump(mode="json"),
        })

    event_bus.subscribe_all(ws_event_broadcaster)

    logger.info("Application startup complete.")

    yield

    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="One-click developer environment manager API.",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom request logger middleware
app.add_middleware(RequestLoggerMiddleware)

# Register error handlers
register_error_handlers(app)

# Include REST API routers
app.include_router(packages.router, prefix=API_V1_PREFIX)
app.include_router(installations.router, prefix=API_V1_PREFIX)
app.include_router(system.router, prefix=API_V1_PREFIX)
app.include_router(environments.router, prefix=API_V1_PREFIX)


@app.get("/")
async def root() -> dict:
    """Root health check endpoint."""
    return {"app": APP_NAME, "version": APP_VERSION, "status": "online"}


@app.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time progress and system event streaming."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
