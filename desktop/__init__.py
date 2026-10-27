"""
Saarthi Desktop Package.
Native Desktop and System-Wide Operating Layer Foundation.
"""

from .app import SaarthiDesktopApp
from .core.state_machine import DesktopStateMachine, DesktopInteractionState
from .core.session_manager import DesktopSessionManager
from .core.pipeline import DesktopCommandPipeline
from .core.settings import DesktopSettingsManager
from .core.privacy import DesktopPrivacyPolicy, privacy_guard

__version__ = "1.0.0-phase3"

__all__ = [
    "SaarthiDesktopApp",
    "DesktopStateMachine",
    "DesktopInteractionState",
    "DesktopSessionManager",
    "DesktopCommandPipeline",
    "DesktopSettingsManager",
    "DesktopPrivacyPolicy",
    "privacy_guard"
]
