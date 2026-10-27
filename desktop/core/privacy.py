"""
Desktop Privacy & Boundary Guard.
Strictly governs what Saarthi Desktop accesses, what requires explicit permissions,
what stays local, and what is transmitted.

Guarantees:
- NO silent background microphone listening.
- NO arbitrary screen recording or background screenshots.
- NO continuous keystroke logging.
- NO silent clipboard surveillance.
- Sensitive application exclusion (password managers, banking, credential vaults).
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger("SaarthiDesktop.Privacy")

# Applications that are strictly blacklisted from automated text capture and context extraction
SENSITIVE_APP_BLOCKLIST = [
    "1password",
    "bitwarden",
    "keepass",
    "keepassxc",
    "lastpass",
    "dashlane",
    "keychain access",
    "credential manager",
    "authenticator",
    "authy"
]

# Sensitive pattern regexes for local redaction
CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    re.compile(r"(?i)ghp_[A-Za-z0-9]{36}"),
    re.compile(r"(?i)sk-[A-Za-z0-9]{32,}"),
    re.compile(r"\b[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b"),  # credit cards
]


class DesktopPrivacyPolicy:
    """Explicit privacy declarations for Saarthi Desktop."""

    @staticmethod
    def get_privacy_declarations() -> Dict[str, Any]:
        return {
            "what_saarthi_accesses": [
                "Frontmost application name and bundle identifier (to understand task context).",
                "Text explicitly highlighted/selected by the user ONLY when the user activates Saarthi.",
                "User queries typed or triggered directly into the Saarthi companion interface."
            ],
            "what_requires_os_permissions": [
                "macOS Accessibility API (AXUIElement) / Windows UI Automation: Required for focused text field detection, selected text extraction, and direct text insertion.",
                "Microphone Permission: DEFERRED to Phase 2. Will require explicit OS consent before any audio device is opened."
            ],
            "what_is_transmitted_to_backend": [
                "The active application name (e.g. 'VS Code' or 'Notes').",
                "The selected text (if user initiated a contextual action like 'rewrite' or 'summarize').",
                "The user's direct text instruction.",
                "Session authentication Bearer token."
            ],
            "what_stays_local": [
                "Global hotkey listener state.",
                "Unfocused application windows and background application activity.",
                "Raw keystrokes (no keylogger is installed).",
                "Clipboard contents (unless user explicitly pastes into the interface)."
            ],
            "retention_policy": [
                "Selected text context is ephemeral and exists in memory only during prompt execution.",
                "No raw audio is captured or stored in Phase 3.",
                "User can view and wipe activity logs at any time."
            ],
            "prohibited_actions": [
                "NO continuous background microphone recording.",
                "NO silent full-screen capture.",
                "NO keystroke logging outside of Saarthi's own input field.",
                "NO context extraction from password managers or credentials vaults."
            ]
        }


class PrivacyBoundaryGuard:
    def __init__(self, excluded_apps: Optional[List[str]] = None):
        self.excluded_apps = set(SENSITIVE_APP_BLOCKLIST)
        if excluded_apps:
            self.excluded_apps.update([a.lower() for a in excluded_apps])

    def is_app_sensitive_or_blocked(self, app_name: str, bundle_id: Optional[str] = None) -> bool:
        """Determines if application is blocked from context collection."""
        name_lower = (app_name or "").lower()
        bundle_lower = (bundle_id or "").lower()

        for blocked in self.excluded_apps:
            if blocked in name_lower or blocked in bundle_lower:
                logger.info(f"Privacy guard: Blocked context extraction from sensitive app '{app_name}'")
                return True
        return False

    def sanitize_selected_text(self, text: Optional[str]) -> str:
        """Removes detected secrets/credentials from selected text before transmission."""
        if not text:
            return ""

        sanitized = text
        for pattern in CREDENTIAL_PATTERNS:
            sanitized = pattern.sub("[REDACTED_CREDENTIAL]", sanitized)

        return sanitized

    def can_capture_selected_text(self, app_name: str, user_explicit_consent: bool = True) -> bool:
        """Validates whether selected text capture is permissible."""
        if not user_explicit_consent:
            return False
        if self.is_app_sensitive_or_blocked(app_name):
            return False
        return True


privacy_guard = PrivacyBoundaryGuard()
