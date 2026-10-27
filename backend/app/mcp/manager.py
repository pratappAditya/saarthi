"""
MCP Server Manager for Saarthi.
Orchestrates MCP server lifecycle, registers discovered tools into Saarthi's central ToolRegistry,
and routes tool calls through the unified policy and permission framework.
"""

import logging
from typing import Dict, Any, List, Optional
from app.mcp.models import (
    MCPServerConfig,
    MCPServerStatus,
    RiskTier,
    TransportType,
    MCPTool
)
from app.mcp.client import MCPClient
from app.intelligence.tools.tool_definition import ToolDefinition, RiskLevel
from app.intelligence.tools.tool_registry import TOOLS_CATALOG

logger = logging.getLogger("app.mcp.manager")


class MCPServerManager:
    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._clients: Dict[str, MCPClient] = {}
        self._init_default_servers()

    def _init_default_servers(self):
        """Seed initial approved integration catalogue."""
        default_research_server = MCPServerConfig(
            id="research-mcp",
            name="Official Research & Docs MCP Server",
            transport=TransportType.STDIO,
            command="mock",
            enabled=True,
            risk_tier=RiskTier.TIER_A
        )
        self.register_server(default_research_server)

    def register_server(self, config: MCPServerConfig) -> bool:
        self._servers[config.id] = config
        self._clients[config.id] = MCPClient(config)
        logger.info(f"Registered MCP server: '{config.id}' ({config.name})")
        return True

    def unregister_server(self, server_id: str) -> bool:
        if server_id in self._clients:
            # Unregister any associated tools from TOOLS_CATALOG
            prefix = f"mcp.{server_id}."
            to_remove = [k for k in TOOLS_CATALOG if k.startswith(prefix)]
            for k in to_remove:
                TOOLS_CATALOG.pop(k, None)
            self._clients.pop(server_id, None)
        if server_id in self._servers:
            self._servers.pop(server_id, None)
            return True
        return False

    def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        return self._servers.get(server_id)

    def list_servers(self) -> List[Dict[str, Any]]:
        return [s.model_dump() for s in self._servers.values()]

    async def connect_and_discover(self, server_id: str) -> List[MCPTool]:
        """Connects to server, discovers its tools, and syncs them to ToolRegistry."""
        client = self._clients.get(server_id)
        if not client:
            logger.warning(f"MCP server '{server_id}' not found.")
            return []

        connected = await client.connect()
        if not connected:
            logger.error(f"Could not connect to MCP server '{server_id}'")
            return []

        tools = await client.list_tools()
        self._sync_tools_to_catalog(server_id, tools, client.config.risk_tier)
        return tools

    def _sync_tools_to_catalog(self, server_id: str, tools: List[MCPTool], server_tier: RiskTier) -> None:
        """Dynamically registers discovered MCP tools into Saarthi's TOOLS_CATALOG."""
        for t in tools:
            canonical_tool_id = f"mcp.{server_id}.{t.name}"
            
            # Map RiskTier to Saarthi RiskLevel
            if t.risk_tier == RiskTier.TIER_A:
                risk_level = RiskLevel.READ_ONLY
                requires_conf = False
                op_type = "OBSERVATION"
            elif t.risk_tier == RiskTier.TIER_B:
                risk_level = RiskLevel.MODERATE
                requires_conf = True
                op_type = "ACTION"
            else:
                risk_level = RiskLevel.CRITICAL
                requires_conf = True
                op_type = "ACTION"

            tool_def = ToolDefinition(
                id=canonical_tool_id,
                name=f"[MCP] {t.name}",
                description=t.description or f"MCP tool from server '{server_id}'",
                input_schema=t.inputSchema,
                required_capability="tools.mcp" if t.risk_tier == RiskTier.TIER_A else "tools.mcp.actions",
                risk_level=risk_level,
                requires_confirmation=requires_conf,
                operation_type=op_type,
                enabled=True
            )
            TOOLS_CATALOG[canonical_tool_id] = tool_def
            logger.info(f"Synchronized MCP tool '{canonical_tool_id}' into ToolRegistry (Risk: {risk_level.value})")

    async def execute_mcp_tool(self, canonical_tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes an MCP tool via its client."""
        parts = canonical_tool_id.split(".", 2)
        if len(parts) != 3 or parts[0] != "mcp":
            return {"success": False, "error": f"Invalid MCP tool identifier: '{canonical_tool_id}'"}

        server_id, tool_name = parts[1], parts[2]
        client = self._clients.get(server_id)
        if not client:
            return {"success": False, "error": f"MCP server '{server_id}' is not registered."}

        if not client.config.enabled:
            return {"success": False, "error": f"MCP server '{server_id}' is currently disabled."}

        # Ensure connected
        if not client._is_connected:
            await client.connect()

        result = await client.call_tool(tool_name, arguments)
        if result.isError:
            err_text = " ".join([c.text for c in result.content if c.text])
            return {"success": False, "error": err_text or "MCP tool execution failed."}

        out_text = "\n".join([c.text for c in result.content if c.text])
        return {
            "success": True,
            "output": out_text,
            "raw_content": [c.model_dump() for c in result.content]
        }


mcp_manager = MCPServerManager()
