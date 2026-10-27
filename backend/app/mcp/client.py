"""
MCP Client Implementation for Saarthi.
Conforms to MCP Specification (2026-07-28) with Modern Streamable HTTP,
Stdio subprocess transport, and explicit tested Legacy (2024-11-05) support.
"""

import json
import inspect
import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional, Union

from app.mcp.models import (
    MCPServerConfig,
    TransportType,
    MCPServerStatus,
    MCPTool,
    MCPResource,
    MCPPrompt,
    CallToolResult,
    ToolContentItem,
    JSONRPCRequest,
    JSONRPCResponse,
    MCPVersion,
    RequestMeta,
    MCPErrorCode,
    ClientInfo
)
import datetime
from app.mcp.policy import MCPPolicy

logger = logging.getLogger("app.mcp.client")


class UnsupportedProtocolVersionError(RuntimeError):
    def __init__(self, message: str, supported: Optional[List[str]] = None):
        super().__init__(message)
        self.supported = supported or []


class MCPClient:
    def __init__(
        self,
        config: MCPServerConfig,
        client_capabilities: Optional[Dict[str, Any]] = None,
        elicitation_handler: Optional[Any] = None
    ):
        self.config = config
        self._request_id = 0
        self._process: Optional[asyncio.subprocess.Process] = None
        self._is_connected = False
        self._server_capabilities: Dict[str, Any] = {}
        self._active_http_tasks: Dict[Union[str, int], asyncio.Task] = {}
        self._detected_era: Optional[str] = None  # "modern", "legacy", or None
        self._probe_retries: int = 0
        self._max_probe_retries: int = 3
        self.client_capabilities = dict(client_capabilities or {})
        self.elicitation_handler = elicitation_handler
        if self.elicitation_handler and "elicitation" not in self.client_capabilities:
            self.client_capabilities["elicitation"] = {}

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def is_modern_http(self) -> bool:
        return self.config.transport in (TransportType.STREAMABLE_HTTP, TransportType.HTTP)

    async def connect(self) -> bool:
        """
        Establishes connection and verifies MCP server.
        - Modern Streamable HTTP: calls server/discover with _meta (no initialize handshake, no session-id).
        - Stdio: initiates subprocess and performs JSON-RPC initialize handshake.
        - Legacy SSE: performs legacy initialize handshake with session-id negotiation.
        """
        valid, err = MCPPolicy.validate_server_config(self.config)
        if not valid:
            self.config.status = MCPServerStatus.FAILED
            self.config.error_message = err
            logger.error(f"Cannot connect to MCP server {self.config.id}: {err}")
            return False

        try:
            if self.config.transport == TransportType.STDIO:
                # Mock or real stdio process
                if self.config.command == "mock":
                    self._is_connected = True
                    self.config.status = MCPServerStatus.CONNECTED
                    self.config.is_live = False
                    self.config.live_verified = False
                    self.config.protocol_version = MCPVersion.LATEST
                    return True

                # Real stdio subprocess
                self.config.is_live = True
                self._process = await asyncio.create_subprocess_exec(
                    self.config.command,
                    *self.config.args,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=self.config.env or None
                )

                # Modern Stdio: Probe with server/discover first (NO initialize handshake if modern)
                # Check process-era cache first
                probe_succeeded = False
                should_fallback_legacy = False

                if self._detected_era == "legacy":
                    should_fallback_legacy = True
                elif self._detected_era == "modern":
                    # Cached modern server
                    probe_succeeded = True
                else:
                    # Enforce bounded probe retry limit
                    if self._probe_retries >= self._max_probe_retries:
                        raise RuntimeError(f"Exceeded maximum probe retries ({self._max_probe_retries}) for stdio server '{self.config.id}'.")

                    self._probe_retries += 1
                    try:
                        discover_res = await self._send_stdio_request(
                            "server/discover",
                            {
                                "_meta": RequestMeta(
                                    protocolVersion=MCPVersion.LATEST,
                                    clientInfo=ClientInfo(name="Saarthi", version="1.0.0"),
                                    clientCapabilities={}
                                ).model_dump()
                            }
                        )
                        if discover_res and isinstance(discover_res, dict):
                            self._server_capabilities = discover_res.get("capabilities", {})
                            server_ver = discover_res.get("protocolVersion", MCPVersion.LATEST)
                            self.config.protocol_version = server_ver if server_ver in MCPVersion.SUPPORTED else MCPVersion.LATEST
                            self._detected_era = "modern"
                            self._is_connected = True
                            self.config.status = MCPServerStatus.CONNECTED
                            self.config.live_verified = True
                            self.config.last_connected_at = datetime.datetime.now(datetime.UTC).isoformat()
                            probe_succeeded = True
                            return True
                    except asyncio.TimeoutError:
                        logger.info("server/discover probe timed out over stdio, attempting legacy fallback")
                        should_fallback_legacy = True
                    except RuntimeError as err:
                        err_str = str(err)
                        # Modern protocol error code -32022 MUST NOT trigger legacy fallback!
                        if "-32022" in err_str or "UnsupportedProtocolVersion" in err_str:
                            logger.error(f"MCP stdio server rejected protocol version with modern -32022: {err}")
                            self._detected_era = "modern"
                            self.config.status = MCPServerStatus.FAILED
                            self.config.error_message = err_str
                            raise
                        # Non-modern errors: -32601 (Method not found), ParseError, or other standard JSON-RPC errors
                        logger.info(f"Modern discovery probe over stdio encountered non-modern error ({err}), falling back to legacy 2024-11-05 handshake...")
                        should_fallback_legacy = True
                    except Exception as ex:
                        if isinstance(ex, TimeoutError):
                            logger.info("server/discover timed out, attempting legacy fallback")
                            should_fallback_legacy = True
                        else:
                            logger.error(f"Unexpected error during modern discovery probe: {ex}")
                            raise

                if should_fallback_legacy and not probe_succeeded:
                    # Legacy 2024-11-05 fallback handshake only for positively identified legacy server
                    init_res = await self._send_stdio_request(
                        "initialize",
                        {
                            "protocolVersion": MCPVersion.LEGACY,
                            "capabilities": {"tools": {}, "resources": {}},
                            "clientInfo": {"name": "Saarthi", "version": "1.0.0"}
                        }
                    )
                    if init_res and "capabilities" in init_res:
                        self._server_capabilities = init_res.get("capabilities", {})
                        self.config.protocol_version = MCPVersion.LEGACY
                        self._detected_era = "legacy"
                        await self._send_notification("notifications/initialized", {})
                        self._is_connected = True
                        self.config.status = MCPServerStatus.CONNECTED
                        self.config.live_verified = True
                        self.config.last_connected_at = datetime.datetime.now(datetime.UTC).isoformat()
                        return True
                    else:
                        self.config.status = MCPServerStatus.DEGRADED
                        return True

            elif self.is_modern_http():
                # Modern Streamable HTTP: NO initialize/notifications/initialized handshake!
                if self.config.url and "mock" in self.config.url:
                    self.config.is_live = False
                    self.config.live_verified = False
                else:
                    self.config.is_live = True

                negotiation_retries = 0
                max_retries = 2
                while negotiation_retries <= max_retries:
                    try:
                        # Modern discovery via 'server/discover'
                        discover_res = await self._send_request("server/discover", {})
                        if discover_res:
                            self._server_capabilities = discover_res.get("capabilities", {})
                            server_ver = discover_res.get("protocolVersion", MCPVersion.LATEST)
                            self.config.protocol_version = server_ver if server_ver in MCPVersion.SUPPORTED else MCPVersion.LATEST
                            self._is_connected = True
                            self.config.status = MCPServerStatus.CONNECTED
                            self.config.live_verified = self.config.is_live
                            self.config.last_connected_at = datetime.datetime.now(datetime.UTC).isoformat()
                            return True
                        else:
                            self.config.status = MCPServerStatus.DEGRADED
                            return True
                    except UnsupportedProtocolVersionError as e:
                        negotiation_retries += 1
                        server_supported = e.supported
                        # Check mutual versions
                        mutual_versions = [v for v in MCPVersion.SUPPORTED if v in server_supported]
                        if not mutual_versions:
                            raise RuntimeError(
                                f"Incompatible MCP protocol version (-32022). Client supports {MCPVersion.SUPPORTED}, Server supports {server_supported}"
                            )

                        # Select highest mutually supported modern version
                        modern_mutual = [v for v in mutual_versions if v != MCPVersion.LEGACY]
                        if modern_mutual and self.config.protocol_version != modern_mutual[0]:
                            self.config.protocol_version = modern_mutual[0]
                            logger.info(f"Retrying connection with mutually supported modern version: {modern_mutual[0]}")
                            continue

                        # If only legacy 2024-11-05 revision is mutually supported
                        if MCPVersion.LEGACY in mutual_versions:
                            logger.info("Server requires legacy 2024-11-05 protocol, falling back to legacy handshake")
                            self.config.protocol_version = MCPVersion.LEGACY
                            init_res = await self._send_legacy_http_request(
                                "initialize",
                                {
                                    "protocolVersion": MCPVersion.LEGACY,
                                    "capabilities": {"tools": {}, "resources": {}},
                                    "clientInfo": {"name": "Saarthi", "version": "1.0.0"}
                                }
                            )
                            if init_res and "capabilities" in init_res:
                                self._server_capabilities = init_res.get("capabilities", {})
                                self._is_connected = True
                                self.config.status = MCPServerStatus.CONNECTED
                                self.config.live_verified = self.config.is_live
                                self.config.last_connected_at = datetime.datetime.now(datetime.UTC).isoformat()
                                return True
                            else:
                                self.config.status = MCPServerStatus.DEGRADED
                                return True

                        raise RuntimeError(f"No usable mutual protocol version found in: {mutual_versions}")

            elif self.config.transport == TransportType.SSE:
                # Deprecated Legacy HTTP+SSE transport
                self.config.is_live = (self.config.url and "mock" not in self.config.url)
                init_res = await self._send_request(
                    "initialize",
                    {
                        "protocolVersion": MCPVersion.LEGACY,
                        "capabilities": {"tools": {}, "resources": {}},
                        "clientInfo": {"name": "Saarthi", "version": "1.0.0"}
                    }
                )
                if init_res and "capabilities" in init_res:
                    self._server_capabilities = init_res.get("capabilities", {})
                    self.config.protocol_version = MCPVersion.LEGACY
                    self._is_connected = True
                    self.config.status = MCPServerStatus.CONNECTED
                    self.config.live_verified = self.config.is_live
                    return True
                else:
                    self.config.status = MCPServerStatus.DEGRADED
                    return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{self.config.id}': {e}")
            self.config.status = MCPServerStatus.FAILED
            self.config.error_message = str(e)
            self._is_connected = False
            if "-32022" in str(e) or "UnsupportedProtocolVersion" in str(e) or "Exceeded maximum probe retries" in str(e):
                raise
            return False

        return False

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Dispatches request across configured transport."""
        if self.config.command == "mock" or (self.config.url and "mock" in self.config.url):
            self._next_id()
            return self._mock_rpc_handler(method, params)

        if self.is_modern_http():
            return await self._send_modern_http_request(method, params)
        elif self.config.transport == TransportType.STDIO:
            return await self._send_stdio_request(method, params)
        elif self.config.transport == TransportType.SSE:
            return await self._send_legacy_http_request(method, params)
        raise ConnectionError(f"Unsupported MCP transport: {self.config.transport}")

    async def _send_modern_http_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Sends modern Streamable HTTP request adhering to MCP 2026-07-28:
        - Includes _meta in request params
        - Sends MCP-Protocol-Version, Mcp-Method, and Mcp-Name (for tools/call) headers
        - Accepts application/json and text/event-stream
        - Does NOT send or maintain protocol-level Mcp-Session-Id
        """
        req_id = self._next_id()
        timeout = min(10.0, self.config.timeout_seconds) if method == "server/discover" else self.config.timeout_seconds

        # Modern _meta injection
        call_params = dict(params or {})
        caps = dict(self.client_capabilities or {})
        if "inputResponses" in call_params:
            caps["elicitation"] = {}

        if "_meta" not in call_params:
            call_params["_meta"] = RequestMeta(
                protocolVersion=self.config.protocol_version or MCPVersion.LATEST,
                clientInfo=ClientInfo(name="Saarthi", version="1.0.0"),
                clientCapabilities=caps
            ).model_dump()

        payload = JSONRPCRequest(id=req_id, method=method, params=call_params).model_dump()

        headers = {
            "MCP-Protocol-Version": self.config.protocol_version or MCPVersion.LATEST,
            "Mcp-Method": method,
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            **self.config.headers
        }
        if method == "tools/call" and params and "name" in params:
            headers["Mcp-Name"] = str(params["name"])

        # Never send session id on modern requests
        headers.pop("Mcp-Session-Id", None)
        headers.pop("mcp-session-id", None)

        current_task = asyncio.current_task()
        if current_task:
            self._active_http_tasks[req_id] = current_task

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(self.config.url, json=payload, headers=headers)
                content_type = resp.headers.get("content-type", "")

                # Version Mismatch / Protocol Error Handling
                if resp.status_code == 400:
                    try:
                        err_data = resp.json()
                        err = err_data.get("error", {})
                        code = err.get("code", 400)
                        msg = err.get("message", resp.text)
                        if code == MCPErrorCode.UNSUPPORTED_PROTOCOL_VERSION:
                            sup = err.get("data", {}).get("supported", []) if isinstance(err.get("data"), dict) else []
                            raise UnsupportedProtocolVersionError(f"UnsupportedProtocolVersion (-32022): {msg}", supported=sup)
                        raise RuntimeError(f"MCP Protocol Error ({code}): {msg}")
                    except UnsupportedProtocolVersionError:
                        raise
                    except Exception as e:
                        if "-32022" in str(e) or "UnsupportedProtocolVersion" in str(e):
                            raise
                        raise RuntimeError(f"MCP Protocol Error HTTP 400: {resp.text}")

                if "text/event-stream" in content_type:
                    # Parse Server-Sent Events stream
                    result_data = None
                    for line in resp.text.splitlines():
                        line = line.strip()
                        if line.startswith("data:"):
                            raw_data = line[5:].strip()
                            if raw_data:
                                event_json = json.loads(raw_data)
                                if "result" in event_json:
                                    result_data = event_json["result"]
                                elif "error" in event_json and event_json["error"]:
                                    raise RuntimeError(f"MCP SSE Error: {event_json['error']}")
                    return result_data

                # Standard application/json response
                data = resp.json()
                if "error" in data and data["error"]:
                    err = data["error"]
                    code = err.get("code", 0)
                    msg = err.get("message", "Unknown error")
                    if code == MCPErrorCode.UNSUPPORTED_PROTOCOL_VERSION:
                        sup = err.get("data", {}).get("supported", []) if isinstance(err.get("data"), dict) else []
                        raise UnsupportedProtocolVersionError(f"UnsupportedProtocolVersion (-32022): {msg}", supported=sup)
                    raise RuntimeError(f"MCP RPC Error ({code}): {msg}")
                return data.get("result")
        finally:
            self._active_http_tasks.pop(req_id, None)

    async def _send_stdio_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        req_id = self._next_id()
        call_params = dict(params or {})
        # Modern 2026-07-28 stdio requests require per-request _meta
        if self.config.protocol_version == MCPVersion.LATEST or method == "server/discover":
            if "_meta" not in call_params:
                call_params["_meta"] = RequestMeta(
                    protocolVersion=MCPVersion.LATEST,
                    clientInfo=ClientInfo(name="Saarthi", version="1.0.0"),
                    clientCapabilities={}
                ).model_dump()

        payload = JSONRPCRequest(id=req_id, method=method, params=call_params).model_dump()
        timeout = min(10.0, self.config.timeout_seconds) if method in ("initialize", "server/discover") else self.config.timeout_seconds

        if not self._process or not self._process.stdin:
            raise ConnectionError("MCP stdio process is not running.")

        req_bytes = (json.dumps(payload) + "\n").encode("utf-8")
        self._process.stdin.write(req_bytes)
        await self._process.stdin.drain()
        line = await asyncio.wait_for(self._process.stdout.readline(), timeout=timeout)
        if not line:
            raise ConnectionError("Empty response from MCP stdio process.")
        resp = json.loads(line.decode("utf-8"))
        if "error" in resp and resp["error"]:
            err = resp["error"]
            code = err.get("code", 0)
            msg = err.get("message", "Unknown error")
            if code == MCPErrorCode.UNSUPPORTED_PROTOCOL_VERSION:
                raise RuntimeError(f"UnsupportedProtocolVersion (-32022): {msg}")
            raise RuntimeError(f"MCP RPC Error ({code}): {msg}")
        return resp.get("result")

    async def _send_legacy_http_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Deprecated legacy HTTP+SSE request maintaining protocol-level Mcp-Session-Id."""
        req_id = self._next_id()
        payload = JSONRPCRequest(id=req_id, method=method, params=params).model_dump()
        headers = {"Content-Type": "application/json", **self.config.headers}
        if self.config.session_id:
            headers["Mcp-Session-Id"] = self.config.session_id

        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            resp = await client.post(self.config.url, json=payload, headers=headers)
            sess_id = resp.headers.get("mcp-session-id") or resp.headers.get("x-session-id")
            if sess_id:
                self.config.session_id = sess_id
            data = resp.json()
            if "error" in data and data["error"]:
                raise RuntimeError(f"Legacy MCP Error: {data['error']}")
            return data.get("result")

    async def cancel_tool_execution(self, request_id: Any, reason: Optional[str] = "User cancelled") -> bool:
        """
        Cancels in-flight tool execution:
        - Modern Streamable HTTP: aborts the client request stream/task directly.
        - Stdio: dispatches JSON-RPC notifications/cancelled notification.
        - Legacy SSE: dispatches legacy notifications/cancelled.
        """
        if self.is_modern_http():
            task = self._active_http_tasks.pop(request_id, None)
            if task and not task.done():
                task.cancel()
                logger.info(f"Closed modern Streamable HTTP stream for request {request_id}")
                return True
            return True

        # Stdio / Legacy SSE notifications/cancelled
        try:
            await self._send_notification("notifications/cancelled", {"requestId": request_id, "reason": reason})
            return True
        except Exception as e:
            logger.warning(f"Failed to send cancellation notification for request {request_id}: {e}")
            return False

    async def _send_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        if self.config.command == "mock":
            return
        payload = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if self.config.transport == TransportType.STDIO and self._process and self._process.stdin:
            self._process.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
            await self._process.stdin.drain()
        elif self.config.transport == TransportType.SSE and self.config.url:
            try:
                headers = {"Content-Type": "application/json", **self.config.headers}
                if self.config.session_id:
                    headers["Mcp-Session-Id"] = self.config.session_id
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(self.config.url, json=payload, headers=headers)
            except Exception as e:
                logger.warning(f"Could not send legacy notification '{method}': {e}")

    def _mock_rpc_handler(self, method: str, params: Optional[Dict[str, Any]]) -> Any:
        """Deterministic mock responses for test environments."""
        if method == "server/discover":
            return {
                "resultType": "complete",
                "protocolVersion": MCPVersion.LATEST,
                "supportedVersions": [MCPVersion.LATEST, MCPVersion.LEGACY],
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": f"MockServer-{self.config.id}", "version": "1.0.0"},
                "ttlMs": 300000,
                "cacheScope": "connection",
                "_meta": {
                    "io.modelcontextprotocol/serverInfo": {
                        "name": f"MockServer-{self.config.id}",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "initialize":
            req_ver = (params or {}).get("protocolVersion", MCPVersion.LEGACY)
            return {
                "protocolVersion": req_ver if req_ver in MCPVersion.SUPPORTED else MCPVersion.LEGACY,
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": f"MockServer-{self.config.id}", "version": "1.0.0"}
            }
        elif method == "tools/list":
            return {
                "resultType": "complete",
                "tools": [
                    {
                        "name": "lookup_docs",
                        "description": "Look up official technical documentation.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"topic": {"type": "string"}},
                            "required": ["topic"]
                        }
                    },
                    {
                        "name": "query_git_metadata",
                        "description": "Query repository branch and commit metadata.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"repo": {"type": "string"}},
                            "required": ["repo"]
                        }
                    }
                ],
                "ttlMs": 60000,
                "cacheScope": "connection",
                "_meta": {
                    "io.modelcontextprotocol/serverInfo": {
                        "name": f"MockServer-{self.config.id}",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "resources/list":
            return {
                "resultType": "complete",
                "resources": [
                    {"uri": f"mcp://{self.config.id}/reference_guide", "name": "Reference Guide", "mimeType": "text/markdown"}
                ],
                "ttlMs": 60000,
                "cacheScope": "connection"
            }
        elif method == "tools/call":
            tool_name = (params or {}).get("name")
            args = (params or {}).get("arguments", {})
            return {
                "resultType": "complete",
                "content": [
                    {
                        "type": "text",
                        "text": f"Successfully executed tool '{tool_name}' with args {json.dumps(args)}."
                    }
                ],
                "isError": False,
                "_meta": {
                    "io.modelcontextprotocol/serverInfo": {
                        "name": f"MockServer-{self.config.id}",
                        "version": "1.0.0"
                    }
                }
            }
        return {}

    async def list_tools(self) -> List[MCPTool]:
        """Discovers tools available on this MCP server."""
        try:
            res = await self._send_request("tools/list")
            raw_tools = (res or {}).get("tools", [])
            tools = []
            for t in raw_tools:
                tier = MCPPolicy.classify_tool_risk(t.get("name", ""), self.config.risk_tier)
                tools.append(
                    MCPTool(
                        name=t.get("name"),
                        description=t.get("description", ""),
                        inputSchema=t.get("inputSchema", {}),
                        server_id=self.config.id,
                        risk_tier=tier
                    )
                )
            self.config.discovered_tools_count = len(tools)
            return tools
        except Exception as e:
            logger.error(f"Failed to list tools from MCP server '{self.config.id}': {e}")
            return []

    async def list_resources(self) -> List[MCPResource]:
        """Discovers resources available on this MCP server."""
        try:
            res = await self._send_request("resources/list")
            raw_res = (res or {}).get("resources", [])
            return [
                MCPResource(
                    uri=r.get("uri"),
                    name=r.get("name"),
                    description=r.get("description"),
                    mimeType=r.get("mimeType"),
                    server_id=self.config.id
                )
                for r in raw_res
            ]
        except Exception as e:
            logger.error(f"Failed to list resources from MCP server '{self.config.id}': {e}")
            return []

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        input_handler: Optional[Any] = None
    ) -> CallToolResult:
        """
        Executes a tool on the MCP server and applies output sanitization.
        Supports Multi Round-Trip Requests (MRTR): if server returns resultType="input_required",
        client validates capabilities, invokes handler to collect inputResponses, and retries
        the operation with a new request ID and echoed requestState.
        """
        try:
            handler = input_handler or self.elicitation_handler
            caps = dict(self.client_capabilities or {})
            if handler:
                caps["elicitation"] = {}

            params = {
                "name": name,
                "arguments": arguments,
                "_meta": RequestMeta(
                    protocolVersion=self.config.protocol_version or MCPVersion.LATEST,
                    clientInfo=ClientInfo(name="Saarthi", version="1.0.0"),
                    clientCapabilities=caps
                ).model_dump()
            }
            res = await self._send_request("tools/call", params)
            res_type = (res or {}).get("resultType", "complete")

            # MRTR Multi Round-Trip Request handling
            if res_type == "input_required":
                input_requests = (res or {}).get("inputRequests", [])
                request_state = (res or {}).get("requestState")

                # Verify client has declared capability for input requests
                for ireq in input_requests:
                    req_method = ireq.get("method") or ireq.get("type")
                    if req_method == "elicitation/create":
                        if not handler or not callable(handler):
                            return CallToolResult(
                                resultType="complete",
                                content=[ToolContentItem(type="text", text="Client does not have required capability 'elicitation' to fulfill input request.")],
                                isError=True
                            )
                    elif req_method not in ("elicitation/create", "sampling/createMessage", "roots/list"):
                        return CallToolResult(
                            resultType="complete",
                            content=[ToolContentItem(type="text", text=f"Unsupported input request method '{req_method}' cannot be fulfilled.")],
                            isError=True
                        )

                if handler and callable(handler):
                    # Invoke user/client input callback
                    responses = await handler(input_requests) if inspect.iscoroutinefunction(handler) else handler(input_requests)
                    # Retry with inputResponses and exact opaque requestState echo
                    retry_params = {
                        "name": name,
                        "arguments": arguments,
                        "inputResponses": responses,
                        "requestState": request_state,
                        "_meta": RequestMeta(
                            protocolVersion=self.config.protocol_version or MCPVersion.LATEST,
                            clientInfo=ClientInfo(name="Saarthi", version="1.0.0"),
                            clientCapabilities=caps
                        ).model_dump()
                    }
                    res = await self._send_request("tools/call", retry_params)
                    res_type = (res or {}).get("resultType", "complete")
                else:
                    return CallToolResult(
                        resultType="input_required",
                        content=[ToolContentItem(type="text", text=(res or {}).get("prompt", "Input required to complete action."))],
                        isError=False
                    )

            if res_type not in ("complete", "input_required"):
                logger.warning(f"Unknown or non-standard MCP resultType received: '{res_type}'")
                return CallToolResult(
                    resultType=res_type,
                    content=[ToolContentItem(type="text", text=f"Unknown or unsupported MCP resultType '{res_type}'")],
                    isError=True
                )

            content_items = []
            for item in (res or {}).get("content", []):
                content_items.append(
                    ToolContentItem(
                        type=item.get("type", "text"),
                        text=item.get("text"),
                        data=item.get("data"),
                        mimeType=item.get("mimeType")
                    )
                )
            result = CallToolResult(
                resultType=res_type,
                content=content_items,
                isError=(res or {}).get("isError", False),
                meta=(res or {}).get("_meta")
            )
            # Apply anti-prompt injection defense
            return MCPPolicy.sanitize_tool_output(result)

        except Exception as e:
            logger.error(f"Error calling MCP tool '{name}' on server '{self.config.id}': {e}")
            return CallToolResult(
                resultType="complete",
                content=[ToolContentItem(type="text", text=f"MCP Execution Error: {str(e)}")],
                isError=True
            )

    async def disconnect(self) -> None:
        """Cleanly disconnects and terminates subprocess if applicable."""
        self._is_connected = False
        self.config.status = MCPServerStatus.DISCONNECTED
        if self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=2.0)
            except Exception:
                pass
            self._process = None
