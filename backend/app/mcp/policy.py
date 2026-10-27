"""
MCP Security Policy and Protection Layer for Saarthi.
Enforces Risk Tier boundaries, anti-SSRF URL filtering, schema verification,
and indirect prompt-injection detection on tool responses.
"""

import re
import urllib.parse
import logging
from typing import Dict, Any, Tuple, Optional
from app.mcp.models import RiskTier, MCPServerConfig, CallToolResult

logger = logging.getLogger("app.mcp.policy")

# Anti-Prompt Injection Detection Patterns in Tool Responses
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+(developer|unrestricted|god)\s+mode", re.IGNORECASE),
    re.compile(r"system\s*:\s*override", re.IGNORECASE),
    re.compile(r"<\s*system\s*>", re.IGNORECASE),
    re.compile(r"assistant\s*:\s*I\s+will\s+now\s+bypass", re.IGNORECASE),
    re.compile(r"disregard\s+the\s+safety\s+policy", re.IGNORECASE),
    re.compile(r"output\s+the\s+api\s*key", re.IGNORECASE),
    re.compile(r"reveal\s+secret", re.IGNORECASE)
]

# SSRF Private IP Ranges
BLOCKED_IP_REGEXES = [
    re.compile(r"^127\."),
    re.compile(r"^localhost$", re.IGNORECASE),
    re.compile(r"^10\."),
    re.compile(r"^192\.168\."),
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\."),
    re.compile(r"^169\.254\."),
    re.compile(r"^0\.0\.0\.0"),
    re.compile(r"^::1")
]


class MCPPolicy:
    @staticmethod
    def validate_server_config(config: MCPServerConfig) -> Tuple[bool, Optional[str]]:
        """Validate server configuration before onboarding."""
        if not config.id or not config.name:
            return False, "Server ID and Name are required."

        transport_val = config.transport.value if hasattr(config.transport, "value") else str(config.transport)
        if transport_val in ("http", "sse", "streamable_http"):
            if not config.url:
                return False, "HTTP/SSE transport requires a valid 'url'."
            parsed = urllib.parse.urlparse(config.url)
            if parsed.scheme not in ("http", "https"):
                return False, "URL scheme must be http or https."
            hostname = (parsed.hostname or "").lower()
            for pat in BLOCKED_IP_REGEXES:
                if pat.search(hostname):
                    logger.warning(f"MCP server URL points to internal IP or metadata host '{hostname}'")
                    return False, f"Security Policy Violation: Server URL cannot point to internal host or cloud metadata IP: {hostname}"

        if transport_val == "stdio":
            if not config.command:
                return False, "Stdio transport requires a 'command' executable."
            # Guard against dangerous direct shell injections in command name
            if any(char in config.command for char in [";", "|", "&", "`", "$"]):
                return False, "Invalid characters in stdio command."

        return True, None

    @staticmethod
    def classify_tool_risk(tool_name: str, server_tier: RiskTier) -> RiskTier:
        """
        Derives tool risk level. If server is Tier C or tool name matches high-risk
        patterns (e.g. exec, shell, db, delete), it escalates to Tier C.
        """
        name_lower = tool_name.lower()
        if any(term in name_lower for term in ["exec", "shell", "terminal", "sql", "db", "delete", "destroy", "deploy"]):
            return RiskTier.TIER_C
        if any(term in name_lower for term in ["write", "create", "update", "patch", "modify", "send", "post"]):
            if server_tier == RiskTier.TIER_C:
                return RiskTier.TIER_C
            return RiskTier.TIER_B
        return server_tier

    @staticmethod
    def sanitize_tool_output(result: CallToolResult) -> CallToolResult:
        """
        Scans tool output for indirect prompt-injection markers and defangs them.
        """
        for item in result.content:
            if item.type == "text" and item.text:
                for pattern in PROMPT_INJECTION_PATTERNS:
                    if pattern.search(item.text):
                        logger.warning(f"Potential indirect prompt injection detected in MCP output! Defanging...")
                        item.text = pattern.sub("[SANITIZED_INSTRUCTION]", item.text)
        return result
