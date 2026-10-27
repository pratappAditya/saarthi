"""
Desktop Interface Abstractions.
Platform-agnostic contracts for desktop integration.
"""

from .context_provider import ApplicationContext, SelectedTextContext, DesktopContextProvider
from .input_provider import DesktopInputType, DesktopInputRequest, DesktopInputProvider
from .shortcut_provider import ShortcutActivationMode, ShortcutConfig, GlobalShortcutProvider
from .accessibility_provider import AccessibilityPermissionStatus, FocusedElementInfo, AccessibilityProvider
from .insertion_provider import InsertionCapabilityStatus, InsertionResult, TextInsertionProvider
from .window_provider import WindowState, WindowGeometry, WindowProvider
from .voice_interfaces import (
    VoiceEnginePhaseStatus,
    AudioChunk,
    TranscriptionEvent,
    SynthesisRequest,
    VoiceInputProvider,
    SpeechRecognitionProvider,
    SpeechSynthesisProvider,
    RealDesktopVoiceEngine,
    UnimplementedVoiceEngine
)

__all__ = [
    "ApplicationContext",
    "SelectedTextContext",
    "DesktopContextProvider",
    "DesktopInputType",
    "DesktopInputRequest",
    "DesktopInputProvider",
    "ShortcutActivationMode",
    "ShortcutConfig",
    "GlobalShortcutProvider",
    "AccessibilityPermissionStatus",
    "FocusedElementInfo",
    "AccessibilityProvider",
    "InsertionCapabilityStatus",
    "InsertionResult",
    "TextInsertionProvider",
    "WindowState",
    "WindowGeometry",
    "WindowProvider",
    "VoiceEnginePhaseStatus",
    "AudioChunk",
    "TranscriptionEvent",
    "SynthesisRequest",
    "VoiceInputProvider",
    "SpeechRecognitionProvider",
    "SpeechSynthesisProvider",
    "RealDesktopVoiceEngine",
    "UnimplementedVoiceEngine"
]
