"""
Normalized Internal Error Codes and Exceptions for Saarthi Agent Runtime.
"""

from enum import Enum
from typing import Optional, Dict, Any

class ErrorCategory(str, Enum):
    MODEL_ERROR = "MODEL_ERROR"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MALFORMED_MODEL_OUTPUT = "MALFORMED_MODEL_OUTPUT"
    TOOL_ERROR = "TOOL_ERROR"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_CANCELLED = "TOOL_CANCELLED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    MEMORY_ERROR = "MEMORY_ERROR"
    SESSION_ERROR = "SESSION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class SaarthiError(Exception):
    """Base exception for all internal Saarthi agent errors."""
    def __init__(
        self,
        category: ErrorCategory,
        message: str,
        user_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.category = category
        self.message = message
        self.user_message = user_message or self._sanitize_user_message(category, message)
        self.details = details or {}
        super().__init__(self.message)

    @staticmethod
    def _sanitize_user_message(category: ErrorCategory, raw_message: str) -> str:
        """Map internal diagnostic error to safe user-facing message without exposing stack traces or secrets."""
        if category == ErrorCategory.MODEL_TIMEOUT:
            return "The request timed out while communicating with the local AI model."
        elif category == ErrorCategory.MODEL_ERROR:
            return "I encountered an error communicating with the local AI model."
        elif category == ErrorCategory.MALFORMED_MODEL_OUTPUT:
            return "The local model produced an unexpected or malformed response format."
        elif category == ErrorCategory.TOOL_TIMEOUT:
            return "The tool execution timed out."
        elif category == ErrorCategory.TOOL_CANCELLED:
            return "Tool execution was cancelled."
        elif category == ErrorCategory.PERMISSION_DENIED:
            return "Tool execution was denied due to security policy."
        elif category == ErrorCategory.PERMISSION_REQUIRED:
            return "User permission confirmation is required to proceed."
        elif category == ErrorCategory.MEMORY_ERROR:
            return "An issue occurred while processing system memory."
        elif category == ErrorCategory.SESSION_ERROR:
            return "Session error occurred."
        elif category == ErrorCategory.TOOL_ERROR:
            return f"Tool execution error: {raw_message}"
        else:
            return "An internal system error occurred. Please try again."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.category.value,
            "message": self.user_message
        }

class InvalidStateTransitionError(SaarthiError):
    def __init__(self, current_state: str, target_state: str):
        super().__init__(
            category=ErrorCategory.INTERNAL_ERROR,
            message=f"Invalid state transition from '{current_state}' to '{target_state}'",
            user_message="An internal state transition error occurred."
        )
        self.current_state = current_state
        self.target_state = target_state
