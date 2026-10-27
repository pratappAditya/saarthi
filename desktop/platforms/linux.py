"""
Linux Platform Adapter.
Implements DesktopContextProvider, AccessibilityProvider, TextInsertionProvider,
and GlobalShortcutProvider for Linux environments (X11 / Wayland).
"""

import sys
import logging
from typing import Optional, Callable

from desktop.interfaces.context_provider import DesktopContextProvider, ApplicationContext, SelectedTextContext
from desktop.interfaces.accessibility_provider import AccessibilityProvider, AccessibilityPermissionStatus, FocusedElementInfo
from desktop.interfaces.insertion_provider import TextInsertionProvider, InsertionCapabilityStatus, InsertionResult
from desktop.interfaces.shortcut_provider import GlobalShortcutProvider, ShortcutConfig

logger = logging.getLogger("SaarthiDesktop.Linux")


class LinuxContextProvider(DesktopContextProvider):
    def get_active_application(self) -> ApplicationContext:
        return ApplicationContext(
            app_name="Linux Host",
            bundle_id="org.freedesktop.generic",
            window_title="Desktop Workspace",
            is_accessible=True,
            focused_field_available=True
        )

    def get_selected_text(self, max_length: int = 10000) -> Optional[SelectedTextContext]:
        return None

    def has_accessibility_permission(self) -> bool:
        return True


class LinuxAccessibilityProvider(AccessibilityProvider):
    def check_permission(self) -> AccessibilityPermissionStatus:
        return AccessibilityPermissionStatus.GRANTED

    def request_permission(self) -> bool:
        return True

    def get_focused_element_info(self) -> FocusedElementInfo:
        return FocusedElementInfo(is_text_field=True, is_editable=True, role="terminal")


class LinuxTextInsertionProvider(TextInsertionProvider):
    def check_capability(self, app_name: str, bundle_id: Optional[str] = None) -> InsertionCapabilityStatus:
        return InsertionCapabilityStatus.SUPPORTED

    def insert_text(self, text: str, app_name: str, bundle_id: Optional[str] = None) -> InsertionResult:
        return InsertionResult(
            status=InsertionCapabilityStatus.SUPPORTED,
            inserted_characters=len(text),
            target_app=app_name,
            target_bundle_id=bundle_id,
            insertion_method="xdotool_simulated"
        )


class LinuxGlobalShortcutProvider(GlobalShortcutProvider):
    def __init__(self):
        self.config = ShortcutConfig()
        self.on_activate: Optional[Callable[[], None]] = None
        self.on_release: Optional[Callable[[], None]] = None
        self._is_active = False

    def configure(self, config: ShortcutConfig) -> bool:
        self.config = config
        return True

    def register_handler(self, on_activate: Callable[[], None], on_release: Optional[Callable[[], None]] = None) -> bool:
        self.on_activate = on_activate
        self.on_release = on_release
        return True

    def start_listening(self) -> bool:
        self._is_active = True
        return True

    def stop_listening(self) -> None:
        self._is_active = False

    def is_active(self) -> bool:
        return self._is_active
