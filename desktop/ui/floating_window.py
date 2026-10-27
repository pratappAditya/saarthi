"""
Floating Window Provider.
Implements WindowProvider using pywebview to render the lightweight FloatingSaarthiUI component.
Handles frameless positioning, top-level windowing, and show/hide transitions.
"""

import sys
import logging
import threading
from typing import Optional

from desktop.interfaces.window_provider import WindowProvider, WindowState, WindowGeometry

logger = logging.getLogger("SaarthiDesktop.FloatingWindow")


class PyWebViewFloatingWindow(WindowProvider):
    def __init__(self, target_url: str = "http://127.0.0.1:8000/?mode=floating", geometry: Optional[WindowGeometry] = None):
        self.target_url = target_url
        self.geometry = geometry or WindowGeometry(width=580, height=440)
        self.state = WindowState.HIDDEN
        self._window = None
        self._webview_thread = None

    def initialize_window(self):
        """Creates the native frameless floating window using pywebview if available."""
        try:
            import webview
            self._window = webview.create_window(
                title="Saarthi Companion",
                url=self.target_url,
                width=self.geometry.width,
                height=self.geometry.height,
                frameless=True,
                easy_drag=True,
                on_top=True,
                resizable=False,
                hidden=True
            )
            self.state = WindowState.HIDDEN
            logger.info("Floating companion window initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize native GUI window (headless/test environment): {e}")
            self._window = None

    def show_floating_window(self) -> bool:
        self.state = WindowState.VISIBLE
        if self._window:
            try:
                self._window.show()
                self._window.restore()
                return True
            except Exception as e:
                logger.error(f"Error showing floating window: {e}")
        return True

    def hide_floating_window(self) -> bool:
        self.state = WindowState.HIDDEN
        if self._window:
            try:
                self._window.hide()
                return True
            except Exception as e:
                logger.error(f"Error hiding floating window: {e}")
        return True

    def toggle_floating_window(self) -> bool:
        if self.state == WindowState.VISIBLE:
            return self.hide_floating_window()
        else:
            return self.show_floating_window()

    def set_position(self, x: int, y: int) -> bool:
        self.geometry.x = x
        self.geometry.y = y
        if self._window:
            try:
                self._window.move(x, y)
                return True
            except Exception:
                pass
        return True

    def get_state(self) -> WindowState:
        return self.state

    def close(self) -> None:
        self.state = WindowState.HIDDEN
        if self._window:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None
