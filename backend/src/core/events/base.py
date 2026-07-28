"""
Base domain event.

All domain events inherit from DomainEvent. Events are the mechanism
by which different parts of the system communicate without coupling:
the installation engine emits events, the WebSocket handler forwards
them to the UI, and the event store persists them for the timeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core.enums import EventSeverity


class DomainEvent(BaseModel):
    """
    Base class for all domain events.

    Domain events represent something meaningful that happened in the
    system. They are immutable records of facts.

    Design principles:
    - Events are past-tense ('InstallationStarted', not 'StartInstallation')
    - Events carry all data needed to understand what happened
    - Events are serializable (Pydantic) for persistence and WebSocket transport
    - Events never contain business logic
    """

    model_config = {"frozen": True}

    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier.")
    event_type: str = Field(..., description="Event class name for deserialization routing.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event occurred.",
    )
    severity: EventSeverity = Field(
        default=EventSeverity.INFO,
        description="Severity level for logging and UI display.",
    )
    correlation_id: UUID | None = Field(
        default=None,
        description="Links related events (e.g., all events from one installation).",
    )
    message: str = Field(
        default="",
        description="Human-readable event description.",
    )

    def model_post_init(self, __context: object) -> None:
        """Auto-set event_type from the class name if not provided."""
        if not self.event_type:
            object.__setattr__(self, "event_type", self.__class__.__name__)
