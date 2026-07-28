"""
Event bus port.

Abstract interface for publishing and subscribing to domain events.
Decouples event producers (engines) from consumers (WebSocket, logging).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any

from src.core.events.base import DomainEvent


# Type alias for event handler callbacks
EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus(ABC):
    """
    Abstract interface for the domain event bus.

    The event bus is the backbone of loose coupling in DevForge:
    - Installation engine emits events
    - WebSocket handler forwards them to the UI
    - Event store persists them for the timeline
    - Logger formats them for structured logging

    None of these components know about each other.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all registered handlers.

        Handlers are invoked asynchronously and independently.
        A failing handler does not prevent other handlers from receiving
        the event.

        Args:
            event: The domain event to publish.
        """

    @abstractmethod
    def subscribe(
        self,
        event_type: type[DomainEvent] | str,
        handler: EventHandler,
    ) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: Event class or event type string to listen for.
            handler: Async callback to invoke when the event is published.
        """

    @abstractmethod
    def subscribe_all(self, handler: EventHandler) -> None:
        """
        Register a handler for all events (catch-all).

        Useful for logging and event store persistence.

        Args:
            handler: Async callback invoked for every event.
        """

    @abstractmethod
    def unsubscribe(
        self,
        event_type: type[DomainEvent] | str,
        handler: EventHandler,
    ) -> None:
        """
        Remove a handler registration.

        Args:
            event_type: Event class or event type string.
            handler: The handler to remove.
        """
