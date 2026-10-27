"""
Model Context Protocol (MCP) Data Models and Schemas for Saarthi.
Conforms to MCP Specification (2026-07-28) with Streamable HTTP and Legacy (2024-11-05) fallback.
Supports JSON-RPC 2.0, Modern Streamable HTTP headers/metadata (_meta), Server Discover,
Tool/Resource discovery, resultType envelopes, and Risk Classification (Tier A, Tier B, Tier C).
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class MCPVersion:
    LATEST = "2026-07-28"
    LEGACY = "2024-11-05"
    SUPPORTED = ["2026-07-28", "2024-11-05"]


class RiskTier(str, Enum):
    TIER_A = "TIER_A"  # Read-only and low-risk (inspection, search, read docs)
    TIER_B = "TIER_B"  # User-approved actions (git branch, workspace file edits)
    TIER_C = "TIER_C"  # High-risk integrations (database, shell, deploy - disabled by default)


class TransportType(str, Enum):
    STREAMABLE_HTTP = "streamable_http"  # Modern Streamable HTTP (2026-07-28)
    HTTP = "http"                       # Standard Streamable HTTP alias
    STDIO = "stdio"                     # Subprocess transport
    SSE = "sse"                         # Deprecated legacy HTTP+SSE transport (2024-11-05)


class MCPServerStatus(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    DISABLED = "DISABLED"


# JSON-RPC 2.0 Baseline
class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class JSONRPCNotification(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    HEADER_MISMATCH = -32020
    MISSING_REQUIRED_CAPABILITY = -32021
    UNSUPPORTED_PROTOCOL_VERSION = -32022


class CoreResultType(str, Enum):
    COMPLETE = "complete"
    INPUT_REQUIRED = "input_required"


# Protocol Metadata & Handshake
class ClientInfo(BaseModel):
    name: str = "Saarthi"
    version: str = "1.0.0"


class ServerInfo(BaseModel):
    name: str
    version: str = "1.0.0"


class ServerCapabilities(BaseModel):
    tools: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None


class UnsupportedProtocolVersionErrorData(BaseModel):
    supported: List[str] = Field(default_factory=lambda: list(MCPVersion.SUPPORTED))
    requested: Optional[str] = None


class MissingRequiredCapabilityErrorData(BaseModel):
    requiredCapabilities: List[str] = Field(default_factory=list)


# Modern 2026-07-28 Request _meta field
# Fully qualified reserved keys per MCP 2026-07-28 specification
class RequestMeta(BaseModel):
    protocolVersion: str = Field(
        default=MCPVersion.LATEST,
        alias="io.modelcontextprotocol/protocolVersion"
    )
    clientCapabilities: Dict[str, Any] = Field(
        default_factory=dict,
        alias="io.modelcontextprotocol/clientCapabilities"
    )
    clientInfo: ClientInfo = Field(
        default_factory=ClientInfo,
        alias="io.modelcontextprotocol/clientInfo"
    )

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


# Legacy Handshake (for positively identified legacy 2024-11-05 servers)
class InitializeRequestParams(BaseModel):
    protocolVersion: str = MCPVersion.LEGACY
    capabilities: Dict[str, Any] = Field(default_factory=lambda: {"tools": {}, "resources": {}})
    clientInfo: ClientInfo = Field(default_factory=ClientInfo)


class InitializeResult(BaseModel):
    protocolVersion: str
    capabilities: ServerCapabilities
    serverInfo: ServerInfo


# Modern 2026-07-28 server/discover result envelope
class ServerDiscoverResult(BaseModel):
    resultType: str = "complete"
    protocolVersion: str = MCPVersion.LATEST
    supportedVersions: List[str] = Field(default_factory=lambda: [MCPVersion.LATEST, MCPVersion.LEGACY])
    capabilities: ServerCapabilities
    serverInfo: ServerInfo
    ttlMs: Optional[int] = 300000
    cacheScope: Optional[str] = "connection"
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


# Tool Definitions
class MCPTool(BaseModel):
    name: str
    description: Optional[str] = ""
    inputSchema: Dict[str, Any] = Field(default_factory=dict)
    server_id: Optional[str] = None
    risk_tier: RiskTier = RiskTier.TIER_A


class MCPResource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None
    server_id: Optional[str] = None


class MCPPrompt(BaseModel):
    name: str
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None
    server_id: Optional[str] = None


class CallToolParams(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ToolContentItem(BaseModel):
    type: str = "text"
    text: Optional[str] = None
    data: Optional[str] = None
    mimeType: Optional[str] = None


# Modern result envelope with core resultType
class CallToolResult(BaseModel):
    resultType: str = "complete"
    content: List[ToolContentItem] = Field(default_factory=list)
    isError: bool = False
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class InputRequest(BaseModel):
    id: str
    method: str = "elicitation/create"  # Supported MRTR methods: elicitation/create, sampling/createMessage, roots/list
    params: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    schema_: Optional[Dict[str, Any]] = Field(default=None, alias="schema")

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class InputResponse(BaseModel):
    id: str
    value: Any = None
    result: Optional[Dict[str, Any]] = None
    cancelled: Optional[bool] = False


class InputRequiredResult(BaseModel):
    resultType: str = "input_required"
    prompt: Optional[str] = ""
    inputRequests: List[InputRequest] = Field(default_factory=list)
    requestState: Optional[str] = None
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class ToolsListResult(BaseModel):
    resultType: str = "complete"
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    ttlMs: Optional[int] = 60000
    cacheScope: Optional[str] = "connection"
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


class ResourcesListResult(BaseModel):
    resultType: str = "complete"
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    ttlMs: Optional[int] = 60000
    cacheScope: Optional[str] = "connection"
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")

    model_config = {
        "populate_by_name": True,
        "serialize_by_alias": True
    }


# Server Configuration & Persistence
class MCPServerConfig(BaseModel):
    id: str
    name: str
    transport: TransportType = TransportType.STREAMABLE_HTTP
    command: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    risk_tier: RiskTier = RiskTier.TIER_A
    status: MCPServerStatus = MCPServerStatus.DISCONNECTED
    last_connected_at: Optional[str] = None
    discovered_tools_count: int = 0
    error_message: Optional[str] = None
    protocol_version: str = MCPVersion.LATEST
    session_id: Optional[str] = None  # Retained only where required by legacy negotiated protocol
    timeout_seconds: float = 30.0
    is_live: bool = False
    live_verified: bool = False
