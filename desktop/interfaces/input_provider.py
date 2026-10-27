"""
Desktop Input Provider Interface.
Defines abstractions for collecting user interaction inputs in the desktop companion.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime


class DesktopInputType(str, Enum):
    TEXT = "TEXT"
    SHORTCUT = "SHORTCUT"
    COMMAND_TRIGGER = "COMMAND_TRIGGER"
    VOICE_DEFERRED = "VOICE_DEFERRED"  # Phase 2 voice placeholder type


class DesktopInputRequest(BaseModel):
    """Encapsulates a user desktop request alongside context."""
    input_type: DesktopInputType = DesktopInputType.TEXT
    content: str
    target_action: Optional[str] = None  # e.g., "rewrite", "explain", "summarize", "custom"
    session_id: str = "desktop_session"
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class DesktopInputProvider(ABC):
    """Abstract provider for receiving user input through desktop controls."""

    @abstractmethod
    def receive_input(self, timeout_seconds: Optional[float] = None) -> Optional[DesktopInputRequest]:
        """Awaits or polls user input from the desktop interaction surface."""
        pass

    @abstractmethod
    def cancel_input(self) -> None:
        """Cancels an active or pending input gathering operation."""
        pass
