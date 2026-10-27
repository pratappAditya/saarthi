"""
Saarthi Desktop Companion Application Runtime.
Orchestrates:
- Tray/Menu-bar presence
- Startup behavior & background process
- Foreground floating companion window
- Show/hide & quit lifecycle
- Global activation shortcuts (Hold & Toggle)
- Active application & selected-text context collection
- Direct text insertion into focused apps
- Authenticated communication with Saarthi backend
"""

import sys
import os
import logging
import threading
from typing import Optional, Dict, Any

from desktop.core.state_machine import DesktopStateMachine, DesktopInteractionState
from desktop.core.session_manager import DesktopSessionManager
from desktop.core.settings import DesktopSettingsManager
from desktop.core.pipeline import DesktopCommandPipeline
from desktop.interfaces.window_provider import WindowProvider, WindowState
from desktop.interfaces.shortcut_provider import ShortcutConfig, ShortcutActivationMode
from desktop.platforms.factory import get_platform_adapters

logger = logging.getLogger("SaarthiDesktop.App")


class SaarthiDesktopApp:
    def __init__(self, backend_url: Optional[str] = None):
        self.settings_manager = DesktopSettingsManager()
        self.backend_url = backend_url or self.settings_manager.settings.backend_url

        self.state_machine = DesktopStateMachine(DesktopInteractionState.IDLE)
        self.session_manager = DesktopSessionManager(backend_base_url=self.backend_url)

        # Initialize Platform-Specific OS Adapters
        (
            self.context_provider,
            self.shortcut_provider,
            self.accessibility_provider,
            self.insertion_provider,
            self.voice_engine
        ) = get_platform_adapters()

        # Initialize Desktop Command Pipeline
        self.pipeline = DesktopCommandPipeline(
            state_machine=self.state_machine,
            session_manager=self.session_manager,
            context_provider=self.context_provider,
            insertion_provider=self.insertion_provider,
            backend_base_url=self.backend_url
        )

        self._window_provider: Optional[WindowProvider] = None
        self._is_running = False
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Configures the global shortcut according to user settings."""
        settings = self.settings_manager.settings
        mode = (
            ShortcutActivationMode.HOLD_TO_ACTIVATE
            if settings.shortcut_mode == "HOLD_TO_ACTIVATE"
            else ShortcutActivationMode.TOGGLE_TO_ACTIVATE
        )

        cfg = ShortcutConfig(
            primary_key=settings.global_shortcut,
            alternative_key=settings.alternative_shortcut,
            mode=mode,
            enabled=True
        )

        self.shortcut_provider.configure(cfg)
        self.shortcut_provider.register_handler(
            on_activate=self.on_shortcut_activated,
            on_release=self.on_shortcut_released if mode == ShortcutActivationMode.HOLD_TO_ACTIVATE else None
        )

    def set_window_provider(self, window_provider: WindowProvider):
        """Attaches the native or webview window provider."""
        self._window_provider = window_provider

    def on_shortcut_activated(self):
        """Invoked when global hotkey (Fn or configurable shortcut) is triggered."""
        logger.info("Global shortcut activation event received.")
        if self.state_machine.current_state == DesktopInteractionState.IDLE:
            self.activate()
        else:
            self.deactivate()

    def on_shortcut_released(self):
        """Invoked when hold-to-activate key is released."""
        logger.info("Global shortcut release event received.")
        # When hold mode is configured, release completes or cancels interaction
        if self.settings_manager.settings.shortcut_mode == "HOLD_TO_ACTIVATE":
            if self.state_machine.current_state in [DesktopInteractionState.READY, DesktopInteractionState.LISTENING]:
                self.deactivate()

    def activate(self) -> Dict[str, Any]:
        """Brings the floating companion to front and gathers active application context."""
        context = self.pipeline.collect_context(include_selected_text=self.settings_manager.settings.selected_text_context)
        self.state_machine.transition_to(
            DesktopInteractionState.READY,
            message="Saarthi ready. How can I help?",
            data={"context": context}
        )

        if self._window_provider:
            self._window_provider.show_floating_window()

        return {"status": "activated", "context": context}

    def deactivate(self):
        """Hides the floating companion and returns to IDLE."""
        self.state_machine.transition_to(
            DesktopInteractionState.IDLE,
            message="Saarthi idle in background."
        )
        if self._window_provider:
            self._window_provider.hide_floating_window()

    def execute_command(
        self,
        prompt: str,
        action: Optional[str] = None,
        auto_insert: bool = False,
        approval_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Processes a desktop user command through the intelligence pipeline."""
        return self.pipeline.execute_request(
            user_prompt=prompt,
            target_action=action,
            auto_insert=auto_insert,
            approval_token=approval_token
        )

    def start(self) -> bool:
        """Starts background listener services and shortcut hooks."""
        self._is_running = True
        self.shortcut_provider.start_listening()
        logger.info("Saarthi Desktop Companion service started successfully.")
        return True

    def stop(self):
        """Stops background listeners and terminates desktop companion process."""
        self._is_running = False
        self.shortcut_provider.stop_listening()
        if self._window_provider:
            self._window_provider.close()
        logger.info("Saarthi Desktop Companion service stopped.")

    def get_status(self) -> Dict[str, Any]:
        """Provides consolidated desktop runtime status."""
        return {
            "is_running": self._is_running,
            "state": self.state_machine.get_summary(),
            "authenticated": self.session_manager.is_authenticated(),
            "active_user": self.session_manager.get_user_info(),
            "accessibility_permission": self.accessibility_provider.check_permission().value,
            "active_application": self.context_provider.get_active_application().model_dump(),
            "shortcut": self.settings_manager.settings.global_shortcut,
            "shortcut_mode": self.settings_manager.settings.shortcut_mode,
            "voice_phase": "PHASE_3_FOUNDATION_VOICE_COMING_IN_PHASE_2",
            "backend_url": self.backend_url
        }
