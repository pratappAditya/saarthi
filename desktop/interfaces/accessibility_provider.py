"""
Accessibility Provider Interface.
Defines abstractions for querying OS accessibility permissions and inspecting UI element properties.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class AccessibilityPermissionStatus(str, Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    NOT_DETERMINED = "NOT_DETERMINED"
    RESTRICTED = "RESTRICTED"


class FocusedElementInfo(BaseModel):
    """Details about the currently focused UI element in the active application."""
    is_text_field: bool = False
    is_editable: bool = False
    role: Optional[str] = None  # e.g., "AXTextArea", "AXTextField"
    current_value_preview: Optional[str] = None
    character_length: int = 0
    app_identifier: Optional[str] = None


class AccessibilityProvider(ABC):
    """Abstract provider for querying accessibility permissions and focused UI elements."""

    @abstractmethod
    def check_permission(self) -> AccessibilityPermissionStatus:
        """Queries OS whether accessibility permissions are granted to Saarthi."""
        pass

    @abstractmethod
    def request_permission(self) -> bool:
        """Prompts the OS accessibility consent dialog if supported."""
        pass

    @abstractmethod
    def get_focused_element_info(self) -> FocusedElementInfo:
        """Inspects the currently focused UI element using OS accessibility APIs."""
        pass
