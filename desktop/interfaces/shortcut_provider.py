"""
Global Shortcut Provider Interface.
Defines abstractions for registering global hotkeys, supporting hold-to-activate and toggle-to-activate.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional, List
from pydantic import BaseModel, Field


class ShortcutActivationMode(str, Enum):
    HOLD_TO_ACTIVATE = "HOLD_TO_ACTIVATE"
    TOGGLE_TO_ACTIVATE = "TOGGLE_TO_ACTIVATE"


class ShortcutConfig(BaseModel):
    """Configuration for global desktop activation shortcut."""
    primary_key: str = "Fn"  # Default shortcut: Fn (macOS globe / Fn), or configurable alternative
    alternative_key: str = "Control+Space"
    modifiers: List[str] = Field(default_factory=list)
    mode: ShortcutActivationMode = ShortcutActivationMode.TOGGLE_TO_ACTIVATE
    hold_threshold_seconds: float = 0.4
    enabled: bool = True


class GlobalShortcutProvider(ABC):
    """Abstract provider for OS-level global shortcut registration and event hooks."""

    @abstractmethod
    def configure(self, config: ShortcutConfig) -> bool:
        """Sets or updates the shortcut configuration."""
        pass

    @abstractmethod
    def register_handler(self, on_activate: Callable[[], None], on_release: Optional[Callable[[], None]] = None) -> bool:
        """Registers callback handlers for shortcut press and release events."""
        pass

    @abstractmethod
    def start_listening(self) -> bool:
        """Begins background monitoring of global hotkeys."""
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        """Stops background hotkey monitoring and frees OS hook resources."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Returns True if the global listener is currently running."""
        pass
