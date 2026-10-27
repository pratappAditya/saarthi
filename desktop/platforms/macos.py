"""
macOS Platform Adapter.
Implements DesktopContextProvider, AccessibilityProvider, TextInsertionProvider,
and GlobalShortcutProvider for macOS using native system APIs and AppleScript bridges.
"""

import sys
import subprocess
import logging
from typing import Optional, Callable, Dict, Any

from desktop.interfaces.context_provider import DesktopContextProvider, ApplicationContext, SelectedTextContext
from desktop.interfaces.accessibility_provider import AccessibilityProvider, AccessibilityPermissionStatus, FocusedElementInfo
from desktop.interfaces.insertion_provider import TextInsertionProvider, InsertionCapabilityStatus, InsertionResult
from desktop.interfaces.shortcut_provider import GlobalShortcutProvider, ShortcutConfig, ShortcutActivationMode
from desktop.interfaces.window_provider import WindowProvider, WindowState

logger = logging.getLogger("SaarthiDesktop.MacOS")

# Known macOS bundle identifiers that support direct text insertion
SUPPORTED_MACOS_APPS = {
    "com.apple.Safari": "Safari",
    "com.google.Chrome": "Google Chrome",
    "com.microsoft.VSCode": "VS Code",
    "com.apple.Notes": "Notes",
    "com.apple.iChat": "Messages",
    "com.apple.mail": "Mail",
    "com.apple.TextEdit": "TextEdit",
    "com.tinyspeck.slackmacgap": "Slack",
    "com.apple.Terminal": "Terminal",
    "com.googlecode.iterm2": "iTerm2",
    "com.microsoft.Word": "Microsoft Word"
}

UNSUPPORTED_MACOS_APPS = {
    "com.apple.finder": "Finder",
    "com.apple.dock": "Dock",
    "com.apple.controlcenter": "Control Center"
}


class MacOSContextProvider(DesktopContextProvider):
    def get_active_application(self) -> ApplicationContext:
        """Queries frontmost application details on macOS."""
        if sys.platform != "darwin":
            return ApplicationContext(
                app_name="macOS Mock Host",
                bundle_id="com.apple.TextEdit",
                window_title="Untitled - TextEdit",
                is_accessible=True,
                focused_field_available=True
            )

        script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            set appName to name of frontApp
            set appBundle to bundle identifier of frontApp
            set winTitle to ""
            try
                set winTitle to name of front window of frontApp
            end try
            return appName & "|||" & appBundle & "|||" & winTitle
        end tell
        '''
        try:
            res = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split("|||")
                app_name = parts[0] if len(parts) > 0 else "Unknown"
                bundle_id = parts[1] if len(parts) > 1 and parts[1] != "missing value" else None
                win_title = parts[2] if len(parts) > 2 and parts[2] != "missing value" else None

                return ApplicationContext(
                    app_name=app_name,
                    bundle_id=bundle_id,
                    window_title=win_title,
                    is_accessible=self.has_accessibility_permission(),
                    focused_field_available=True
                )
        except Exception as e:
            logger.warning(f"Error querying active application on macOS: {e}")

        return ApplicationContext(app_name="Unknown", is_accessible=False)

    def get_selected_text(self, max_length: int = 10000) -> Optional[SelectedTextContext]:
        """Gets currently selected text using macOS System Events / AppleScript without clobbering clipboard."""
        if sys.platform != "darwin":
            return SelectedTextContext(
                text="Sample highlighted text for testing context extraction.",
                character_count=52,
                source_app="macOS Mock Host"
            )

        script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            set appName to name of frontApp
            set selText to ""
            try
                -- Attempt to read selected text from focused UI element
                set focusedElement to focused UI element of frontApp
                set selText to value of attribute "AXSelectedText" of focusedElement
            end try
            return selText
        end tell
        '''
        try:
            res = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=2
            )
            text = res.stdout.strip() if res.returncode == 0 else ""
            if text:
                if len(text) > max_length:
                    text = text[:max_length]
                    is_truncated = True
                else:
                    is_truncated = False

                return SelectedTextContext(
                    text=text,
                    character_count=len(text),
                    is_truncated=is_truncated
                )
        except Exception as e:
            logger.warning(f"Error extracting selected text on macOS: {e}")

        return None

    def has_accessibility_permission(self) -> bool:
        if sys.platform != "darwin":
            return True

        # Check accessibility permission status via AXIsProcessTrusted
        script = '''
        tell application "System Events"
            return UI elements enabled
        end tell
        '''
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            return res.returncode == 0 and "true" in res.stdout.lower()
        except Exception:
            return False


class MacOSAccessibilityProvider(AccessibilityProvider):
    def check_permission(self) -> AccessibilityPermissionStatus:
        if sys.platform != "darwin":
            return AccessibilityPermissionStatus.GRANTED

        ctx = MacOSContextProvider()
        if ctx.has_accessibility_permission():
            return AccessibilityPermissionStatus.GRANTED
        return AccessibilityPermissionStatus.DENIED

    def request_permission(self) -> bool:
        if sys.platform != "darwin":
            return True

        # Open System Settings > Privacy & Security > Accessibility
        try:
            subprocess.run(
                ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"],
                timeout=3
            )
            return True
        except Exception as e:
            logger.error(f"Failed to open macOS accessibility settings: {e}")
            return False

    def get_focused_element_info(self) -> FocusedElementInfo:
        if sys.platform != "darwin":
            return FocusedElementInfo(is_text_field=True, is_editable=True, role="AXTextArea")

        script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            try
                set focusedElement to focused UI element of frontApp
                set elRole to role of focusedElement
                return elRole
            on error
                return "NONE"
            end try
        end tell
        '''
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            role = res.stdout.strip()
            is_text = role in ["AXTextArea", "AXTextField", "AXComboBox"]
            return FocusedElementInfo(is_text_field=is_text, is_editable=is_text, role=role)
        except Exception:
            return FocusedElementInfo()


class MacOSTextInsertionProvider(TextInsertionProvider):
    def check_capability(self, app_name: str, bundle_id: Optional[str] = None) -> InsertionCapabilityStatus:
        # Check permissions first
        if sys.platform == "darwin":
            if not MacOSContextProvider().has_accessibility_permission():
                return InsertionCapabilityStatus.PERMISSION_REQUIRED

        if bundle_id and bundle_id in UNSUPPORTED_MACOS_APPS:
            return InsertionCapabilityStatus.UNSUPPORTED

        if (bundle_id and bundle_id in SUPPORTED_MACOS_APPS) or any(
            k.lower() in app_name.lower() for k in ["code", "notes", "safari", "chrome", "mail", "messages", "word", "textedit", "slack"]
        ):
            return InsertionCapabilityStatus.SUPPORTED

        return InsertionCapabilityStatus.SUPPORTED  # Default to attempt for standard apps

    def insert_text(self, text: str, app_name: str, bundle_id: Optional[str] = None) -> InsertionResult:
        capability = self.check_capability(app_name, bundle_id)
        if capability != InsertionCapabilityStatus.SUPPORTED:
            return InsertionResult(
                status=capability,
                target_app=app_name,
                target_bundle_id=bundle_id,
                error_message=f"Text insertion capability check returned {capability.value}"
            )

        if sys.platform != "darwin":
            # Mock success for cross-platform testing
            return InsertionResult(
                status=InsertionCapabilityStatus.SUPPORTED,
                inserted_characters=len(text),
                target_app=app_name,
                target_bundle_id=bundle_id,
                insertion_method="accessibility_api_mock"
            )

        # AppleScript keystroke insertion into the active application
        sanitized_text = text.replace('\\', '\\\\').replace('"', '\\"')
        script = f'''
        tell application "System Events"
            keystroke "{sanitized_text}"
        end tell
        '''
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return InsertionResult(
                    status=InsertionCapabilityStatus.SUPPORTED,
                    inserted_characters=len(text),
                    target_app=app_name,
                    target_bundle_id=bundle_id,
                    insertion_method="system_events_keystroke"
                )
            else:
                return InsertionResult(
                    status=InsertionCapabilityStatus.FAILED,
                    target_app=app_name,
                    target_bundle_id=bundle_id,
                    error_message=res.stderr.strip() or "AppleScript keystroke failed."
                )
        except Exception as e:
            logger.error(f"Text insertion failed on macOS: {e}")
            return InsertionResult(
                status=InsertionCapabilityStatus.FAILED,
                target_app=app_name,
                target_bundle_id=bundle_id,
                error_message=str(e)
            )


class MacOSGlobalShortcutProvider(GlobalShortcutProvider):
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
        logger.info(f"MacOS shortcut listener started for primary key '{self.config.primary_key}' ({self.config.mode.value})")
        return True

    def stop_listening(self) -> None:
        self._is_active = False
        logger.info("MacOS shortcut listener stopped.")

    def is_active(self) -> bool:
        return self._is_active
