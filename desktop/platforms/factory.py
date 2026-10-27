"""
Platform Adapter Factory.
Automatically instantiates the appropriate OS-specific providers based on sys.platform.
"""

import sys
from typing import Tuple

from desktop.interfaces.context_provider import DesktopContextProvider
from desktop.interfaces.shortcut_provider import GlobalShortcutProvider
from desktop.interfaces.accessibility_provider import AccessibilityProvider
from desktop.interfaces.insertion_provider import TextInsertionProvider
from desktop.interfaces.voice_interfaces import UnimplementedVoiceEngine, RealDesktopVoiceEngine

from desktop.platforms.macos import (
    MacOSContextProvider,
    MacOSGlobalShortcutProvider,
    MacOSAccessibilityProvider,
    MacOSTextInsertionProvider
)
from desktop.platforms.windows import (
    WindowsContextProvider,
    WindowsGlobalShortcutProvider,
    WindowsAccessibilityProvider,
    WindowsTextInsertionProvider
)
from desktop.platforms.linux import (
    LinuxContextProvider,
    LinuxGlobalShortcutProvider,
    LinuxAccessibilityProvider,
    LinuxTextInsertionProvider
)


def get_platform_adapters() -> Tuple[
    DesktopContextProvider,
    GlobalShortcutProvider,
    AccessibilityProvider,
    TextInsertionProvider,
    UnimplementedVoiceEngine
]:
    """Returns the matching platform providers for the active host OS."""
    voice_engine = RealDesktopVoiceEngine()

    if sys.platform == "darwin":
        return (
            MacOSContextProvider(),
            MacOSGlobalShortcutProvider(),
            MacOSAccessibilityProvider(),
            MacOSTextInsertionProvider(),
            voice_engine
        )
    elif sys.platform == "win32":
        return (
            WindowsContextProvider(),
            WindowsGlobalShortcutProvider(),
            WindowsAccessibilityProvider(),
            WindowsTextInsertionProvider(),
            voice_engine
        )
    else:
        return (
            LinuxContextProvider(),
            LinuxGlobalShortcutProvider(),
            LinuxAccessibilityProvider(),
            LinuxTextInsertionProvider(),
            voice_engine
        )
