"""
Event handlers bridging domain events to WebSockets and event log store.
"""

from __future__ import annotations

from src.core.events.base import DomainEvent
from src.database.repositories.sqlite_event_log_repo import SqliteEventLogRepository
from src.database.session import get_session_factory
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("events.handlers")


async def persist_event_handler(event: DomainEvent) -> None:
    """
    Catch-all handler that persists published domain events into the SQLite event log table.
    """
    try:
        factory = get_session_factory()
        async with factory() as session:
            repo = SqliteEventLogRepository(session)
            await repo.save_event(event)
    except Exception as exc:
        logger.debug(f"Failed to persist event '{event.event_type}': {exc}")
