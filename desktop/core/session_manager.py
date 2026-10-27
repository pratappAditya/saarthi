"""
Desktop Session Manager.
Handles authentication, token persistence, and session synchronization with Saarthi Backend.
Enforces security: No backend secrets stored in desktop client, only user session token.
Supports logout propagation and account switching.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

logger = logging.getLogger("SaarthiDesktop.SessionManager")


class DesktopSessionManager:
    def __init__(self, backend_base_url: str = "http://127.0.0.1:8000", session_dir: Optional[str] = None):
        self.backend_base_url = backend_base_url.rstrip("/")
        if session_dir is None:
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
            session_dir = os.path.join(local_appdata, "Saarthi", "desktop_session")
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)
        self.session_file = os.path.join(self.session_dir, "session.json")
        self._cached_session: Optional[Dict[str, Any]] = None
        self._load_cached_session()

    def _load_cached_session(self):
        """Loads cached session token from local storage."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "session_token" in data:
                        self._cached_session = data
            except Exception as e:
                logger.error(f"Failed to read cached session file: {e}")
                self._cached_session = None

    def _save_session_file(self, session_data: Dict[str, Any]):
        """Persists session data to local client storage."""
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2)
            self._cached_session = session_data
        except Exception as e:
            logger.error(f"Failed to persist session to file: {e}")

    def get_token(self) -> Optional[str]:
        """Returns the current active Bearer session token, if available."""
        if self._cached_session:
            return self._cached_session.get("session_token")
        return None

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Returns cached user profile info."""
        if self._cached_session:
            return self._cached_session.get("user")
        return None

    def is_authenticated(self) -> bool:
        """Checks if a valid token is locally available and non-empty."""
        token = self.get_token()
        return bool(token and len(token) > 5)

    def login(self, email: str, password: str, device_name: str = "Saarthi Desktop Companion") -> Dict[str, Any]:
        """Authenticates with backend and stores session token."""
        url = f"{self.backend_base_url}/api/auth/login"
        payload = json.dumps({
            "email": email,
            "password": password,
            "device_id": f"desktop_{os.getlogin() if hasattr(os, 'getlogin') else 'user'}",
            "device_name": device_name
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("status") == "success" and "session" in result:
                    token = result["session"]["session_token"]
                    user = result.get("user", {})
                    save_payload = {
                        "session_token": token,
                        "user": user,
                        "session_id": result["session"].get("session_id"),
                        "email": email
                    }
                    self._save_session_file(save_payload)
                    return {"success": True, "user": user, "token": token}
                else:
                    return {"success": False, "error": "Invalid login response format"}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            logger.warning(f"Login failed HTTP {e.code}: {error_body}")
            try:
                detail = json.loads(error_body).get("detail", str(e))
            except Exception:
                detail = error_body or str(e)
            return {"success": False, "error": detail, "code": e.code}
        except Exception as e:
            logger.error(f"Login network error: {e}")
            return {"success": False, "error": f"Connection error: {str(e)}"}

    def validate_session(self) -> Dict[str, Any]:
        """
        Validates the stored session against backend /api/auth/me.
        If expired or revoked, purges local cache and notifies.
        """
        token = self.get_token()
        if not token:
            return {"valid": False, "reason": "No active session token"}

        url = f"{self.backend_base_url}/api/auth/me"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "SaarthiDesktop/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    # Update cached user info
                    if self._cached_session and "user" in data:
                        self._cached_session["user"] = data["user"]
                        self._save_session_file(self._cached_session)
                    return {"valid": True, "user": data.get("user"), "quota": data.get("quota")}
                return {"valid": False, "reason": f"Unexpected HTTP status {resp.status}"}
        except urllib.error.HTTPError as e:
            if e.code in [401, 403]:
                logger.info("Stored session is expired or revoked. Clearing local session.")
                self.logout(notify_backend=False)
                return {"valid": False, "reason": "Session expired or revoked", "code": e.code}
            return {"valid": False, "reason": f"HTTP error {e.code}", "code": e.code}
        except Exception as e:
            logger.warning(f"Backend connectivity check failed during session validation: {e}")
            return {"valid": False, "reason": f"Backend unreachable: {str(e)}", "offline": True}

    def logout(self, notify_backend: bool = True) -> bool:
        """Revokes session on backend if online and purges local storage."""
        token = self.get_token()
        if notify_backend and token:
            url = f"{self.backend_base_url}/api/auth/logout"
            req = urllib.request.Request(
                url,
                data=b"{}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=3):
                    pass
            except Exception as e:
                logger.warning(f"Could not notify backend of logout: {e}")

        self._cached_session = None
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
            except Exception as e:
                logger.error(f"Error removing session file: {e}")
        return True

    def switch_account(self, new_email: str, new_password: str) -> Dict[str, Any]:
        """Switches current desktop session to a different account."""
        self.logout(notify_backend=True)
        return self.login(new_email, new_password)
