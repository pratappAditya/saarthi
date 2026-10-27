"""
Window Provider Interface.
Defines abstractions for managing the floating Saarthi companion window (positioning, show/hide, visibility).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple
from pydantic import BaseModel


class WindowState(str, Enum):
    HIDDEN = "HIDDEN"
    VISIBLE = "VISIBLE"
    MINIMIZED = "MINIMIZED"
    PINNED = "PINNED"


class WindowGeometry(BaseModel):
    width: int = 540
    height: int = 380
    x: Optional[int] = None
    y: Optional[int] = None


class WindowProvider(ABC):
    """Abstract provider for managing the floating companion GUI window."""

    @abstractmethod
    def show_floating_window(self) -> bool:
        """Brings the floating companion window to the foreground."""
        pass

    @abstractmethod
    def hide_floating_window(self) -> bool:
        """Hides the companion window without terminating the background process."""
        pass

    @abstractmethod
    def toggle_floating_window(self) -> bool:
        """Toggles visibility between hidden and foreground."""
        pass

    @abstractmethod
    def set_position(self, x: int, y: int) -> bool:
        """Reposition the floating window on the display."""
        pass

    @abstractmethod
    def get_state(self) -> WindowState:
        """Queries the current window visibility state."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Closes and releases window resources."""
        pass
