"""
Desktop Context Provider Interface.
Defines abstractions for querying the active application and selected text.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime


class ApplicationContext(BaseModel):
    """Structured context of the currently active/focused desktop application."""
    app_name: str = "Unknown Application"
    bundle_id: Optional[str] = None  # e.g., com.apple.Safari or com.microsoft.VSCode
    window_title: Optional[str] = None
    process_id: Optional[int] = None
    is_accessible: bool = False
    focused_field_available: bool = False
    focused_field_type: Optional[str] = None  # e.g., "AXTextArea", "EDIT", "RichText"
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class SelectedTextContext(BaseModel):
    """Structured context representing text selected by the user in the active application."""
    text: str = ""
    character_count: int = 0
    source_app: Optional[str] = None
    source_bundle_id: Optional[str] = None
    is_truncated: bool = False
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class DesktopContextProvider(ABC):
    """Abstract provider for querying active application and system desktop context."""

    @abstractmethod
    def get_active_application(self) -> ApplicationContext:
        """Retrieves structured context for the currently active/frontmost application."""
        pass

    @abstractmethod
    def get_selected_text(self, max_length: int = 10000) -> Optional[SelectedTextContext]:
        """Retrieves currently selected text in the active application without clipboard pollution where possible."""
        pass

    @abstractmethod
    def has_accessibility_permission(self) -> bool:
        """Returns True if the OS has granted accessibility permissions to Saarthi Desktop."""
        pass
