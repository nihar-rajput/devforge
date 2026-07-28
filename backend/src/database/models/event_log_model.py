"""
SQLAlchemy ORM model for domain event store / event log.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import EventSeverity
from src.core.events.base import DomainEvent
from src.database.session import Base


class EventLogModel(Base):
    """
    SQLAlchemy ORM model for event_log table.

    Persists all domain events published via the EventBus for audit history,
    troubleshooting, and timeline visualization in the dashboard.
    """

    __tablename__ = "event_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=EventSeverity.INFO.value, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    @classmethod
    def from_domain_event(cls, event: DomainEvent) -> EventLogModel:
        """
        Convert a DomainEvent to an EventLogModel record.

        The complete Pydantic model is serialized to JSON in payload_json.
        """
        payload = event.model_dump_json()
        return cls(
            event_id=str(event.event_id),
            event_type=event.event_type,
            severity=event.severity.value,
            correlation_id=str(event.correlation_id) if event.correlation_id else None,
            message=event.message,
            payload_json=payload,
            timestamp=event.timestamp,
        )

    def get_payload_dict(self) -> dict:
        """Return the parsed payload JSON dictionary."""
        return json.loads(self.payload_json)
