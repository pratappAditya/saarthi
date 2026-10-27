import os
import json
import datetime
from typing import Dict, Any, List
from app.tools.registry import ToolRegistry
from app.security.permissions import SecurityManager, PermissionLevel
from app.security.paths import is_path_allowed, normalize_file_path
from app.config.settings import settings

class ToolExecutor:
    def __init__(self, registry: ToolRegistry, security_manager: SecurityManager, allowed_roots: List[str], log_path: str, timeout: float = None):
        self.registry = registry
        self.security_manager = security_manager
        self.allowed_roots = allowed_roots
        self.log_path = log_path
        self.timeout = timeout if timeout is not None else getattr(settings, "TOOL_EXECUTION_TIMEOUT", 30.0)
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    def _filter_secrets(self, d: Any) -> Any:
        """
        Recursively screens arguments to mask potential passwords, keys, or tokens.
        """
        if isinstance(d, dict):
            filtered = {}
            secret_keywords = ["key", "password", "token", "secret", "auth", "credential", "private"]
            for k, v in d.items():
                if any(kw in k.lower() for kw in secret_keywords):
                    filtered[k] = "[REDACTED]"
                else:
                    filtered[k] = self._filter_secrets(v)
            return filtered
        elif isinstance(d, list):
            return [self._filter_secrets(item) for item in d]
        elif isinstance(d, str):
            # Mask potential tokens or long secrets containing no spaces
            if len(d) > 30 and not " " in d:
                return "[REDACTED_POTENTIAL_SECRET]"
            return d
        return d

    def _log_execution(self, session_id: str, tool_name: str, permission_level: PermissionLevel, arguments: dict, confirmed: bool, status: str, error_code: str = None, duration: float = None):
        """
        Writes a structured JSON-line log entry to the log file.
        """
        import datetime
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Determine approval status string
        if permission_level in [PermissionLevel.READ_ONLY, PermissionLevel.SAFE]:
            approval_status = "automatically_approved"
        elif confirmed:
            approval_status = "approved"
        elif status == "pending_confirmation":
            approval_status = "pending"
        else:
            approval_status = "denied"

        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id or "default_session",
            "tool": tool_name,
            "permission_level": permission_level.value if hasattr(permission_level, 'value') else str(permission_level),
            "approval_status": approval_status,
            "arguments": self._filter_secrets(arguments),
            "confirmation_required": permission_level in [PermissionLevel.USER_CONFIRMATION, PermissionLevel.PRIVILEGED],
            "confirmed": confirmed,
            "status": status,
            "error_code": error_code,
            "duration": duration
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            # Prevent logging failure from crashing the execution service, print to stdout as fallback
            print(f"Warning: Failed to write to tool execution log: {str(e)}")

    async def execute_tool(self, name: str, arguments: dict, session_id: str = "default_session", confirmed: bool = False) -> dict:
        # 1. Lookup Tool
        tool = self.registry.get(name)
        if not tool:
            self._log_execution(session_id, name, PermissionLevel.SAFE, arguments, confirmed, "failure", "TOOL_NOT_FOUND")
            return {
                "success": False,
                "tool": name,
                "error": {
                    "code": "TOOL_NOT_FOUND",
                    "message": f"Tool '{name}' is not registered in the Tool System."
                }
            }

        # 2. Normalize and check path arguments for path traversal
        path_keys = ["path", "filepath", "directory", "target", "root_path"]
        for key, value in arguments.items():
            if key in path_keys and isinstance(value, str) and value.strip():
                normalized_value = normalize_file_path(value)
                # Mutate arguments in-place so tools receive normalized paths
                arguments[key] = normalized_value
                if not is_path_allowed(normalized_value, self.allowed_roots):
                    self._log_execution(session_id, name, tool.permission_level, arguments, confirmed, "failure", "PATH_TRAVERSAL_DENIED")
                    return {
                        "success": False,
                        "tool": name,
                        "error": {
                            "code": "PATH_TRAVERSAL_DENIED",
                            "message": f"Access to path '{value}' is denied. It lies outside the allowed workspace."
                        }
                    }


        # 3. Check safety level permissions
        required_level = tool.permission_level
        
        # Enforce user confirmations on required permission levels
        if required_level == PermissionLevel.USER_CONFIRMATION:
            if not confirmed:
                self._log_execution(session_id, name, required_level, arguments, confirmed, "pending_confirmation", "CONFIRMATION_REQUIRED")
                return {
                    "success": False,
                    "tool": name,
                    "status": "pending_confirmation",
                    "error": {
                        "code": "CONFIRMATION_REQUIRED",
                        "message": f"Tool '{name}' requires user confirmation before execution."
                    }
                }
        elif required_level == PermissionLevel.PRIVILEGED:
            # Privileged actions are immediately rejected for now
            self._log_execution(session_id, name, required_level, arguments, confirmed, "failure", "PERMISSION_DENIED")
            return {
                "success": False,
                "tool": name,
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": f"Tool '{name}' requires PRIVILEGED safety level which is currently rejected."
                }
            }

        # Enforce check through SecurityManager safety levels
        if not self.security_manager.is_allowed(required_level):
            self._log_execution(session_id, name, required_level, arguments, confirmed, "failure", "PERMISSION_DENIED")
            return {
                "success": False,
                "tool": name,
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": f"Tool '{name}' safety level ({required_level}) exceeds current safety level settings."
                }
            }

        # 4. Execute tool
        import time
        import asyncio
        import inspect
        start_time = time.perf_counter()
        try:
            is_sync_flag = getattr(tool, "is_synchronous", False)
            is_coro = inspect.iscoroutinefunction(tool.execute)

            if not is_coro:
                exec_coro = asyncio.to_thread(tool.execute, **arguments)
            elif is_sync_flag and hasattr(tool, "_execute_sync"):
                exec_coro = asyncio.to_thread(getattr(tool, "_execute_sync"), **arguments)
            else:
                exec_coro = tool.execute(**arguments)

            if self.timeout and self.timeout > 0:
                result = await asyncio.wait_for(exec_coro, timeout=self.timeout)
            else:
                result = await exec_coro

            duration = time.perf_counter() - start_time
            self._log_execution(session_id, name, required_level, arguments, confirmed, "success", duration=duration)
            return {
                "success": True,
                "tool": name,
                "data": result
            }
        except asyncio.TimeoutError:
            duration = time.perf_counter() - start_time
            self._log_execution(session_id, name, required_level, arguments, confirmed, "failure", "TOOL_TIMEOUT", duration=duration)
            return {
                "success": False,
                "tool": name,
                "error": {
                    "code": "TOOL_TIMEOUT",
                    "message": f"Tool '{name}' execution timed out after {self.timeout} seconds."
                }
            }
        except Exception as e:
            duration = time.perf_counter() - start_time
            # Map exception details cleanly
            self._log_execution(session_id, name, required_level, arguments, confirmed, "failure", "EXECUTION_ERROR", duration=duration)
            
            # Determine appropriate code
            code = "EXECUTION_ERROR"
            if isinstance(e, FileNotFoundError):
                code = "FILE_NOT_FOUND"
            elif isinstance(e, PermissionError):
                code = "PERMISSION_DENIED"
            elif isinstance(e, ValueError):
                code = "INVALID_ARGUMENT"
                
            return {
                "success": False,
                "tool": name,
                "error": {
                    "code": code,
                    "message": str(e)
                }
            }
