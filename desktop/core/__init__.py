"""
Desktop Core Package.
Contains platform-agnostic state machine, session management, privacy boundaries,
settings, and command pipeline.
"""

from .state_machine import DesktopStateMachine, DesktopInteractionState
from .session_manager import DesktopSessionManager
from .privacy import DesktopPrivacyPolicy, PrivacyBoundaryGuard, privacy_guard
from .settings import DesktopSettingsManager, DesktopSettingsModel
from .pipeline import DesktopCommandPipeline

__all__ = [
    "DesktopStateMachine",
    "DesktopInteractionState",
    "DesktopSessionManager",
    "DesktopPrivacyPolicy",
    "PrivacyBoundaryGuard",
    "privacy_guard",
    "DesktopSettingsManager",
    "DesktopSettingsModel",
    "DesktopCommandPipeline"
]
