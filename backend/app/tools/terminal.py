import os
import re
import subprocess
from typing import Dict, Any
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel
from app.config.settings import settings
from app.security.paths import is_path_allowed

class TerminalTool(BaseTool):
    @property
    def name(self) -> str:
        return "terminal"

    @property
    def description(self) -> str:
        return "Execute an approved PowerShell command within the workspace directory."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.USER_CONFIRMATION

    @property
    def risk_classification(self) -> str:
        return "HIGH"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The PowerShell command to run."
                }
            },
            "required": ["command"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "stdout": {
                    "type": "string",
                    "description": "Standard output from the command execution."
                },
                "stderr": {
                    "type": "string",
                    "description": "Standard error output from the command execution."
                },
                "exit_code": {
                    "type": "integer",
                    "description": "The command exit code."
                }
            }
        }

    def validate_command(self, command: str):
        if not command or not command.strip():
            raise ValueError("Command cannot be empty.")

        # Block chaining and multi-commands
        if ";" in command:
            raise PermissionError("Command chaining with ';' is blocked for safety.")
        if "&" in command:
            raise PermissionError("Command chaining/background running with '&' is blocked for safety.")
        if "\n" in command or "\r" in command:
            raise PermissionError("Multi-line commands are blocked for safety.")

        # Deletion safety patterns (specific refusal message)
        deletion_patterns = [
            r"\brm\b", r"\bdel\b", r"\berase\b", r"\brd\b", r"\brmdir\b",
            r"remove-item", r"remove-itemproperty"
        ]
        for pattern in deletion_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                raise PermissionError("File deletion is not currently enabled in Saarthi...")

        # Destructive patterns (case-insensitive checks)
        # Block cmdlets: Format-Volume, Format-Disk, Initialize-Disk, Clear-Disk, Stop-Computer, Restart-Computer, Get-Credential, Set-ItemProperty, New-Item
        # Block aliases/executables: format, diskpart, shutdown, reg, net, cmdkey, vaultcmd
        blocked_patterns = [
            r"\bformat\b", r"\bdiskpart\b", r"\bshutdown\b", r"\breg\b",
            r"\bnet\b", r"\bcmdkey\b", r"\bvaultcmd\b",
            r"format-volume", r"format-disk", r"initialize-disk",
            r"clear-disk", r"stop-computer", r"restart-computer", r"get-credential",
            r"set-itemproperty", r"new-item"
        ]

        for pattern in blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                raise PermissionError(f"Command contains blocked pattern '{pattern}' and is classified as PRIVILEGED.")


    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, command: str, **kwargs) -> Any:
        import asyncio
        return await asyncio.to_thread(self._execute_sync, command=command, **kwargs)

    def _execute_sync(self, command: str, **kwargs) -> Any:
        # Validate the command against security policies
        self.validate_command(command)

        # Restrict working directory to E:\Saarthi or configured root
        cwd = settings.TOOL_ROOT_PATH
        if not os.path.exists(cwd):
            os.makedirs(cwd, exist_ok=True)

        if not is_path_allowed(cwd, settings.ALLOWED_ROOTS):
            raise PermissionError(f"Working directory '{cwd}' is outside the allowed sandbox roots.")

        # Always run using powershell.exe with profile/interactive disabled
        args = [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            command
        ]

        try:
            # Run PowerShell command with configured timeout
            proc = subprocess.run(
                args,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=settings.TERMINAL_TIMEOUT_SECONDS
            )
            stdout = proc.stdout
            stderr = proc.stderr
            exit_code = proc.returncode
        except subprocess.TimeoutExpired as e:
            stdout = e.stdout.decode("utf-8", errors="ignore") if e.stdout else ""
            stderr = (e.stderr.decode("utf-8", errors="ignore") if e.stderr else "") + f"\n[Command timed out after {settings.TERMINAL_TIMEOUT_SECONDS} seconds]"
            exit_code = -1
        except Exception as e:
            raise RuntimeError(f"Failed to execute command: {str(e)}")

        # Enforce output length limit
        max_chars = settings.MAX_TOOL_OUTPUT_CHARS
        if len(stdout) > max_chars:
            stdout = stdout[:max_chars] + f"\n\n[STDOUT TRUNCATED TO {max_chars} CHARACTERS]"
        if len(stderr) > max_chars:
            stderr = stderr[:max_chars] + f"\n\n[STDERR TRUNCATED TO {max_chars} CHARACTERS]"

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code
        }

