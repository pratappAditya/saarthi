"""
Desktop Settings Manager.
Handles configuration for:
- launch on startup
- global shortcut (Fn / alternative)
- desktop notifications
- active-app integration
- accessibility permission status
- privacy controls
- selected-text handling
- desktop session/logout
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("SaarthiDesktop.Settings")


class DesktopSettingsModel(BaseModel):
    launch_on_startup: bool = True
    global_shortcut: str = "Fn"
    alternative_shortcut: str = "Control+Space"
    shortcut_mode: str = "TOGGLE_TO_ACTIVATE"  # "TOGGLE_TO_ACTIVATE" or "HOLD_TO_ACTIVATE"
    desktop_notifications: bool = True
    active_app_integration: bool = True
    selected_text_context: bool = True
    privacy_mode_strict: bool = True
    excluded_apps: List[str] = Field(default_factory=lambda: [
        "1Password", "Bitwarden", "KeePass", "Keychain Access"
    ])
    backend_url: str = "http://127.0.0.1:8000"


class DesktopSettingsManager:
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            config_dir = os.path.join(local_appdata, "Saarthi", "desktop_config")
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        self.settings = self._load()

    def _load(self) -> DesktopSettingsModel:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return DesktopSettingsModel(**data)
            except Exception as e:
                logger.error(f"Failed to load desktop settings: {e}. Using defaults.")
        return DesktopSettingsModel()

    def save(self) -> bool:
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings.model_dump(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save desktop settings: {e}")
            return False

    def update(self, updates: Dict[str, Any]) -> DesktopSettingsModel:
        current_dict = self.settings.model_dump()
        for k, v in updates.items():
            if k in current_dict:
                current_dict[k] = v
        self.settings = DesktopSettingsModel(**current_dict)
        self.save()
        return self.settings

    def to_dict(self) -> Dict[str, Any]:
        return self.settings.model_dump()
