"""
SQLite repository for persistent event logging and timeline queries.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import EventSeverity
from src.core.events.base import DomainEvent
from src.database.models.event_log_model import EventLogModel


class SqliteEventLogRepository:
    """
    Concrete repository for saving and querying persistent domain events.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_event(self, event: DomainEvent) -> None:
        """Persist a domain event to the database."""
        model = EventLogModel.from_domain_event(event)
        self._session.add(model)
        await self._session.commit()

    async def get_by_correlation_id(self, correlation_id: UUID) -> list[EventLogModel]:
        """Get all event records associated with a correlation ID."""
        stmt = (
            select(EventLogModel)
            .where(EventLogModel.correlation_id == str(correlation_id))
            .order_by(EventLogModel.timestamp.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent(
        self,
        limit: int = 100,
        min_severity: EventSeverity | None = None,
    ) -> list[EventLogModel]:
        """Get recent log records, optionally filtered by minimum severity."""
        stmt = select(EventLogModel).order_by(EventLogModel.timestamp.desc()).limit(limit)
        if min_severity:
            stmt = stmt.where(EventLogModel.severity == min_severity.value)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_older_than_days(self, days: int) -> int:
        """Prune old event log entries."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(EventLogModel).where(EventLogModel.timestamp < cutoff)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount or 0
