"""
Desktop Platforms Package.
Provides OS adapters for macOS, Windows, and Linux.
"""

from .factory import get_platform_adapters
from .macos import MacOSContextProvider, MacOSAccessibilityProvider, MacOSTextInsertionProvider, MacOSGlobalShortcutProvider
from .windows import WindowsContextProvider, WindowsAccessibilityProvider, WindowsTextInsertionProvider, WindowsGlobalShortcutProvider
from .linux import LinuxContextProvider, LinuxAccessibilityProvider, LinuxTextInsertionProvider, LinuxGlobalShortcutProvider

__all__ = [
    "get_platform_adapters",
    "MacOSContextProvider",
    "MacOSAccessibilityProvider",
    "MacOSTextInsertionProvider",
    "MacOSGlobalShortcutProvider",
    "WindowsContextProvider",
    "WindowsAccessibilityProvider",
    "WindowsTextInsertionProvider",
    "WindowsGlobalShortcutProvider",
    "LinuxContextProvider",
    "LinuxAccessibilityProvider",
    "LinuxTextInsertionProvider",
    "LinuxGlobalShortcutProvider"
]
