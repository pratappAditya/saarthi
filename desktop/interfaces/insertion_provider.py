"""
Text Insertion Provider Interface.
Defines abstractions for securely inserting generated text into the active compatible application.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class InsertionCapabilityStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    FAILED = "FAILED"


class InsertionResult(BaseModel):
    """Result returned after an insertion attempt."""
    status: InsertionCapabilityStatus
    inserted_characters: int = 0
    target_app: str = "Unknown"
    target_bundle_id: Optional[str] = None
    error_message: Optional[str] = None
    insertion_method: str = "accessibility_api"  # "accessibility_api", "keystroke_simulation", "clipboard_paste"


class TextInsertionProvider(ABC):
    """Abstract provider for injecting text into the currently focused application element."""

    @abstractmethod
    def check_capability(self, app_name: str, bundle_id: Optional[str] = None) -> InsertionCapabilityStatus:
        """Determines if the active application and focused element support text insertion."""
        pass

    @abstractmethod
    def insert_text(self, text: str, app_name: str, bundle_id: Optional[str] = None) -> InsertionResult:
        """Attempts to insert text into the active focused field. Returns structured InsertionResult."""
        pass
