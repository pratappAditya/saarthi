"""
Desktop Command Pipeline.
Orchestrates the complete flow:
DESKTOP ACTIVATION
-> CONTEXT COLLECTION (Active App + Selected Text)
-> USER INPUT
-> SAARTHI API (/api/desktop/command & /api/unified/chat)
-> INTENT & PERSONALIZATION & DOMAIN ROUTING
-> TASK/AGENT ENGINE
-> PERMISSION VERIFICATION
-> RESULT
-> DESKTOP OUTPUT / DIRECT TEXT INSERTION

Guarantees:
- Never bypasses PermissionStore / server-side verification.
- Direct text insertion uses capability detection (SUPPORTED, UNSUPPORTED, PERMISSION_REQUIRED, FAILED).
- Reflects state changes via DesktopStateMachine.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

from desktop.core.state_machine import DesktopStateMachine, DesktopInteractionState
from desktop.core.session_manager import DesktopSessionManager
from desktop.core.privacy import privacy_guard
from desktop.interfaces.context_provider import DesktopContextProvider, ApplicationContext, SelectedTextContext
from desktop.interfaces.insertion_provider import TextInsertionProvider, InsertionCapabilityStatus, InsertionResult

logger = logging.getLogger("SaarthiDesktop.Pipeline")


class DesktopCommandPipeline:
    def __init__(
        self,
        state_machine: DesktopStateMachine,
        session_manager: DesktopSessionManager,
        context_provider: DesktopContextProvider,
        insertion_provider: TextInsertionProvider,
        backend_base_url: str = "http://127.0.0.1:8000"
    ):
        self.state_machine = state_machine
        self.session_manager = session_manager
        self.context_provider = context_provider
        self.insertion_provider = insertion_provider
        self.backend_base_url = backend_base_url.rstrip("/")

    def collect_context(self, include_selected_text: bool = True) -> Dict[str, Any]:
        """
        Step 1: Collects frontmost application context and optional highlighted text.
        Applies privacy guard sanitization and blocklists.
        """
        app_ctx = self.context_provider.get_active_application()

        # Check privacy guard for sensitive applications
        is_sensitive = privacy_guard.is_app_sensitive_or_blocked(
            app_name=app_ctx.app_name,
            bundle_id=app_ctx.bundle_id
        )

        selected_text_val: Optional[str] = None
        if include_selected_text and not is_sensitive and privacy_guard.can_capture_selected_text(app_ctx.app_name):
            sel_ctx = self.context_provider.get_selected_text()
            if sel_ctx and sel_ctx.text:
                selected_text_val = privacy_guard.sanitize_selected_text(sel_ctx.text)

        return {
            "active_application": app_ctx.model_dump(),
            "is_sensitive_app": is_sensitive,
            "selected_text": selected_text_val,
            "has_accessibility_permission": self.context_provider.has_accessibility_permission()
        }

    def execute_request(
        self,
        user_prompt: str,
        target_action: Optional[str] = None,  # "rewrite", "explain", "summarize", "translate", "custom"
        auto_insert: bool = False,
        approval_token: Optional[str] = None,
        context_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Step 2-10: Executes the user request through Saarthi backend intelligence.
        """
        self.state_machine.transition_to(
            DesktopInteractionState.PROCESSING,
            message="Gathering application context and preparing query..."
        )

        # 1. Collect desktop context
        context = context_override or self.collect_context(include_selected_text=True)

        # 2. Check Authentication
        token = self.session_manager.get_token()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SaarthiDesktopCompanion/1.0"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 3. Transition to THINKING while waiting for intelligence response
        self.state_machine.transition_to(
            DesktopInteractionState.THINKING,
            message="Saarthi Intelligence analyzing request..."
        )

        # 4. Prepare request payload
        payload = {
            "prompt": user_prompt,
            "action": target_action or "chat",
            "active_application": context.get("active_application", {}),
            "selected_text": context.get("selected_text"),
            "approval_token": approval_token,
            "auto_insert_requested": auto_insert
        }

        url = f"{self.backend_base_url}/api/desktop/command"
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Desktop API returned HTTP {e.code}: {err_body}")
            self.state_machine.transition_to(
                DesktopInteractionState.ERROR,
                message=f"Backend Error (HTTP {e.code})",
                error=err_body
            )
            return {"success": False, "status": "error", "error": err_body, "code": e.code}
        except urllib.error.URLError as e:
            logger.error(f"Backend connection failed: {e}")
            self.state_machine.transition_to(
                DesktopInteractionState.ERROR,
                message="Saarthi backend unavailable. Ensure service is running.",
                error=str(e)
            )
            return {"success": False, "status": "error", "error": "Backend unreachable", "offline": True}
        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}", exc_info=True)
            self.state_machine.transition_to(
                DesktopInteractionState.ERROR,
                message=f"Pipeline exception: {str(e)}",
                error=str(e)
            )
            return {"success": False, "status": "error", "error": str(e)}

        # 5. Check if action requires permission approval
        if result.get("status") == "pending_confirmation" or result.get("awaiting_confirmation"):
            perm_req = result.get("permission_request", {})
            self.state_machine.transition_to(
                DesktopInteractionState.READY,
                message="Action requires explicit permission confirmation.",
                data={"permission_request": perm_req}
            )
            return {
                "success": True,
                "status": "pending_confirmation",
                "permission_request": perm_req,
                "message": result.get("message") or result.get("response")
            }

        # 6. Check for Direct Text Insertion if requested
        generated_text = result.get("response") or result.get("message", "")
        insertion_result: Optional[InsertionResult] = None

        if auto_insert and generated_text:
            app_name = context.get("active_application", {}).get("app_name", "Unknown")
            bundle_id = context.get("active_application", {}).get("bundle_id")

            # Check capability first
            capability = self.insertion_provider.check_capability(app_name, bundle_id)
            if capability == InsertionCapabilityStatus.SUPPORTED:
                insertion_result = self.insertion_provider.insert_text(generated_text, app_name, bundle_id)
            else:
                insertion_result = InsertionResult(
                    status=capability,
                    target_app=app_name,
                    target_bundle_id=bundle_id,
                    error_message=f"Target application {app_name} insertion capability is {capability.value}"
                )

        # 7. Transition to COMPLETED
        self.state_machine.transition_to(
            DesktopInteractionState.COMPLETED,
            message="Task completed successfully.",
            data={
                "result": result,
                "insertion": insertion_result.model_dump() if insertion_result else None
            }
        )

        return {
            "success": True,
            "status": "completed",
            "result": result,
            "response": generated_text,
            "insertion": insertion_result.model_dump() if insertion_result else None
        }
