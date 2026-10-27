"""
MCP Management and Protocol Endpoints for Saarthi.
Provides administrative controls for MCP server onboarding, connection testing,
tool discovery inspection, and the public/authenticated MCP JSON-RPC gateway.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

from app.mcp.models import MCPServerConfig, TransportType, RiskTier
from app.mcp.manager import mcp_manager
from app.mcp.server import saarthi_mcp_server

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])


class RegisterServerRequest(BaseModel):
    id: str
    name: str
    transport: TransportType = TransportType.STDIO
    command: Optional[str] = None
    args: List[str] = []
    env: Dict[str, str] = {}
    url: Optional[str] = None
    headers: Dict[str, str] = {}
    enabled: bool = True
    risk_tier: RiskTier = RiskTier.TIER_A


@router.get("/servers")
def list_mcp_servers():
    """Lists all registered MCP servers with operational statuses."""
    return {"servers": mcp_manager.list_servers()}


@router.post("/servers")
def register_mcp_server(req: RegisterServerRequest):
    """Registers an MCP server and pre-validates transport configuration."""
    config = MCPServerConfig(**req.model_dump())
    success = mcp_manager.register_server(config)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to register MCP server.")
    return {"status": "registered", "server": config.model_dump()}


@router.delete("/servers/{server_id}")
def delete_mcp_server(server_id: str):
    """Removes an MCP server and de-registers its associated tools."""
    removed = mcp_manager.unregister_server(server_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found.")
    return {"status": "removed", "server_id": server_id}


@router.post("/servers/{server_id}/toggle")
def toggle_mcp_server(server_id: str, enabled: bool):
    """Enables or disables an MCP server without deleting configuration."""
    server = mcp_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found.")
    server.enabled = enabled
    return {"status": "updated", "server_id": server_id, "enabled": enabled}


@router.post("/servers/{server_id}/test")
async def test_and_discover_tools(server_id: str):
    """Connects to server, runs handshake, and discovers available tools/resources."""
    server = mcp_manager.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found.")
    tools = await mcp_manager.connect_and_discover(server_id)
    return {
        "status": "connected",
        "server_id": server_id,
        "tools_discovered": len(tools),
        "tools": [t.model_dump() for t in tools]
    }


@router.get("/tools")
def list_discovered_mcp_tools():
    """Lists all active MCP tools registered in Saarthi's central catalog."""
    from app.intelligence.tools.tool_registry import ToolRegistry
    all_tools = ToolRegistry.list_tools()
    mcp_tools = [t for t in all_tools if t["id"].startswith("mcp.")]
    return {"mcp_tools": mcp_tools, "total": len(mcp_tools)}


from fastapi import Response

@router.post("/rpc")
async def handle_mcp_rpc(
    request: Dict[str, Any],
    response: Response,
    authorization: Optional[str] = Header(None),
    mcp_protocol_version: Optional[str] = Header(None, alias="MCP-Protocol-Version"),
    mcp_method: Optional[str] = Header(None, alias="Mcp-Method"),
    mcp_name: Optional[str] = Header(None, alias="Mcp-Name")
):
    """
    JSON-RPC 2.0 endpoint for external clients interacting with Saarthi MCP Server.
    Conforms to MCP Specification (2026-07-28) Streamable HTTP.
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    # Enforce transport authentication per MCP HTTP authorization specification
    if saarthi_mcp_server.auth_token and not saarthi_mcp_server.verify_auth(token):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized MCP access",
            headers={"WWW-Authenticate": 'Bearer realm="MCP"'}
        )

    headers = {}
    if mcp_protocol_version:
        headers["MCP-Protocol-Version"] = mcp_protocol_version
    if mcp_method:
        headers["Mcp-Method"] = mcp_method
    if mcp_name:
        headers["Mcp-Name"] = mcp_name

    res = await saarthi_mcp_server.handle_request(request, client_token=token, headers=headers)
    response.headers["MCP-Protocol-Version"] = "2026-07-28"

    if "error" in res and res["error"]:
        err_code = res["error"].get("code", 0)
        # MCP 2026-07-28 Streamable HTTP status code mapping:
        # -32022 (UnsupportedProtocolVersion), -32020 (HeaderMismatch), -32021 (MissingRequiredCapability),
        # -32600 (InvalidRequest), -32602 (InvalidParams), -32700 (ParseError) -> HTTP 400
        # -32601 (MethodNotFound) -> HTTP 404
        # Application-level / standard tool errors -> HTTP 200 (retaining JSON-RPC error envelope)
        if err_code in (-32022, -32020, -32021, -32600, -32602, -32700):
            response.status_code = 400
        elif err_code == -32601:
            response.status_code = 404
        else:
            response.status_code = 200

    return res
