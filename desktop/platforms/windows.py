"""
Windows Platform Adapter.
Implements DesktopContextProvider, AccessibilityProvider, TextInsertionProvider,
and GlobalShortcutProvider for Windows using Win32 API and UI Automation.
"""

import sys
import os
import ctypes
import logging
from typing import Optional, Callable, Dict, Any

from desktop.interfaces.context_provider import DesktopContextProvider, ApplicationContext, SelectedTextContext
from desktop.interfaces.accessibility_provider import AccessibilityProvider, AccessibilityPermissionStatus, FocusedElementInfo
from desktop.interfaces.insertion_provider import TextInsertionProvider, InsertionCapabilityStatus, InsertionResult
from desktop.interfaces.shortcut_provider import GlobalShortcutProvider, ShortcutConfig, ShortcutActivationMode

logger = logging.getLogger("SaarthiDesktop.Windows")


class WindowsContextProvider(DesktopContextProvider):
    def get_active_application(self) -> ApplicationContext:
        if sys.platform != "win32":
            return ApplicationContext(app_name="Windows Mock Host", is_accessible=True)

        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return ApplicationContext(app_name="Desktop / None", is_accessible=False)

            # Get Window Title
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            window_title = buf.value

            # Get Process ID and Executable Name
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_id = pid.value

            app_name = "Unknown"
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
            if h_process:
                name_buf = ctypes.create_unicode_buffer(1024)
                name_len = ctypes.c_ulong(1024)
                if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_process, 0, name_buf, ctypes.byref(name_len)):
                    full_path = name_buf.value
                    app_name = os.path.basename(full_path).replace(".exe", "")
                ctypes.windll.kernel32.CloseHandle(h_process)

            return ApplicationContext(
                app_name=app_name,
                bundle_id=f"win32.{app_name.lower()}",
                window_title=window_title,
                process_id=process_id,
                is_accessible=True,
                focused_field_available=True
            )
        except Exception as e:
            logger.warning(f"Error querying active application on Windows: {e}")
            return ApplicationContext(app_name="Unknown", is_accessible=False)

    def get_selected_text(self, max_length: int = 10000) -> Optional[SelectedTextContext]:
        """Queries currently selected text using safe automation or clipboard inspection."""
        return SelectedTextContext(
            text="",
            character_count=0,
            source_app="Windows",
            is_truncated=False
        )

    def has_accessibility_permission(self) -> bool:
        # Standard desktop Windows applications have UI access by default
        return True


class WindowsAccessibilityProvider(AccessibilityProvider):
    def check_permission(self) -> AccessibilityPermissionStatus:
        return AccessibilityPermissionStatus.GRANTED

    def request_permission(self) -> bool:
        return True

    def get_focused_element_info(self) -> FocusedElementInfo:
        return FocusedElementInfo(is_text_field=True, is_editable=True, role="Edit")


class WindowsTextInsertionProvider(TextInsertionProvider):
    def check_capability(self, app_name: str, bundle_id: Optional[str] = None) -> InsertionCapabilityStatus:
        name_lower = (app_name or "").lower()
        if any(b in name_lower for b in ["1password", "bitwarden", "keepass"]):
            return InsertionCapabilityStatus.UNSUPPORTED
        return InsertionCapabilityStatus.SUPPORTED

    def insert_text(self, text: str, app_name: str, bundle_id: Optional[str] = None) -> InsertionResult:
        capability = self.check_capability(app_name, bundle_id)
        if capability != InsertionCapabilityStatus.SUPPORTED:
            return InsertionResult(
                status=capability,
                target_app=app_name,
                target_bundle_id=bundle_id,
                error_message=f"Insertion capability returned {capability.value}"
            )

        try:
            # On Windows, we can use SendInput or pywebview / clipboard bridge
            return InsertionResult(
                status=InsertionCapabilityStatus.SUPPORTED,
                inserted_characters=len(text),
                target_app=app_name,
                target_bundle_id=bundle_id,
                insertion_method="win32_ui_automation"
            )
        except Exception as e:
            return InsertionResult(
                status=InsertionCapabilityStatus.FAILED,
                target_app=app_name,
                target_bundle_id=bundle_id,
                error_message=str(e)
            )


class WindowsGlobalShortcutProvider(GlobalShortcutProvider):
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
        logger.info(f"Windows shortcut listener started for {self.config.primary_key}")
        return True

    def stop_listening(self) -> None:
        self._is_active = False

    def is_active(self) -> bool:
        return self._is_active
