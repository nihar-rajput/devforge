"""
In-process async event bus implementation.

Implements EventBus port for decoupled event publishing and handler subscription.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Type

from src.core.events.base import DomainEvent
from src.core.ports.event_bus import EventBus, EventHandler
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("events.bus")


class DefaultEventBus(EventBus):
    """
    In-process async event bus.
    Handlers run asynchronously without blocking the event producer.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._catch_all_handlers: List[EventHandler] = []

    async def publish(self, event: DomainEvent) -> None:
        """Publish event to registered handlers."""
        event_type_name = event.event_type

        # Collect handlers
        target_handlers = self._handlers.get(event_type_name, []) + self._catch_all_handlers

        if not target_handlers:
            return

        for handler in target_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as exc:
                logger.error(f"Error in event handler '{handler.__name__}' for event '{event_type_name}': {exc}")

    def subscribe(
        self,
        event_type: Type[DomainEvent] | str,
        handler: EventHandler,
    ) -> None:
        type_str = event_type.__name__ if isinstance(event_type, type) else str(event_type)
        if type_str not in self._handlers:
            self._handlers[type_str] = []
        if handler not in self._handlers[type_str]:
            self._handlers[type_str].append(handler)
            logger.debug(f"Subscribed '{handler.__name__}' to event '{type_str}'")

    def subscribe_all(self, handler: EventHandler) -> None:
        if handler not in self._catch_all_handlers:
            self._catch_all_handlers.append(handler)
            logger.debug(f"Subscribed catch-all handler '{handler.__name__}'")

    def unsubscribe(
        self,
        event_type: Type[DomainEvent] | str,
        handler: EventHandler,
    ) -> None:
        type_str = event_type.__name__ if isinstance(event_type, type) else str(event_type)
        if type_str in self._handlers and handler in self._handlers[type_str]:
            self._handlers[type_str].remove(handler)
