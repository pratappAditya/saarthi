import os
import re
import json
import uuid
import time
import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from app.models.factory import ModelFactory
from app.memory.sqlite import SQLiteMemoryProvider
from app.memory.manager import memory_manager, MemoryRequest, MemoryApprovalRequiredException
from app.memory.commands import MemoryCommandProcessor
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor
from app.tools.file_list import FileListTool
from app.tools.file_read import FileReadTool
from app.tools.file_search import FileSearchTool
from app.tools.system_info import SystemInfoTool
from app.tools.terminal import TerminalTool
from app.tools.suggest_memory import SuggestMemoryTool
from app.security.permissions import SecurityManager, PermissionLevel, PermissionRequiredException, PermissionRequest
from app.config.settings import settings
from app.agent.errors import InvalidStateTransitionError, ErrorCategory, SaarthiError


def validate_arguments(schema: dict, args: dict) -> None:
    if not isinstance(args, dict):
        raise ValueError("Arguments must be a key-value dictionary.")
        
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    # Check required arguments
    for req in required:
        if req not in args:
            raise ValueError(f"Missing required argument: '{req}'")
            
    # Check argument types and names
    for key, value in args.items():
        if key not in properties:
            raise ValueError(f"Unknown argument: '{key}'")
            
        prop_schema = properties[key]
        expected_type = prop_schema.get("type")
        
        if expected_type == "string" and not isinstance(value, str):
            raise ValueError(f"Argument '{key}' must be a string.")
        elif expected_type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"Argument '{key}' must be a boolean.")
        elif expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            raise ValueError(f"Argument '{key}' must be an integer.")
        elif expected_type == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
            raise ValueError(f"Argument '{key}' must be a number.")
        elif expected_type == "array" and not isinstance(value, list):
            raise ValueError(f"Argument '{key}' must be a list.")
        elif expected_type == "object" and not isinstance(value, dict):
            raise ValueError(f"Argument '{key}' must be a dictionary.")


ALLOWED_STATE_TRANSITIONS = {
    "IDLE": {"RUNNING", "CANCELLED"},
    "RUNNING": {"WAITING_MODEL", "WAITING_TOOL", "EXECUTING_TOOL", "CANCELLED", "FAILED", "RUNNING", "IDLE"},
    "WAITING_MODEL": {"RUNNING", "COMPLETED", "WAITING_PERMISSION", "WAITING_TOOL", "FAILED", "TIMEOUT", "CANCELLED"},
    "WAITING_PERMISSION": {"RUNNING", "CANCELLED", "EXECUTING_TOOL", "WAITING_TOOL"},
    "WAITING_TOOL": {"EXECUTING_TOOL", "WAITING_PERMISSION", "CANCELLED", "FAILED", "RUNNING", "WAITING_TOOL"},
    "EXECUTING_TOOL": {"RUNNING", "WAITING_TOOL", "EXECUTING_TOOL", "FAILED", "TIMEOUT", "CANCELLED"},
    "COMPLETED": {"IDLE", "RUNNING"},
    "FAILED": {"IDLE", "RUNNING"},
    "CANCELLED": {"IDLE", "RUNNING"},
    "TIMEOUT": {"RUNNING", "FAILED", "CANCELLED", "IDLE"},
}


@dataclass
class AgentState:
    session_id: str
    request_id: str
    user_request: str
    iteration: int = 0
    selected_tool: Optional[str] = None
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    pending_permission: Optional[Dict[str, Any]] = None
    retrieved_memories: List[Dict[str, Any]] = field(default_factory=list)
    current_state: str = "IDLE"
    errors: List[str] = field(default_factory=list)
    called_tools: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.perf_counter)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"))
    updated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"))
    state_history: List[Dict[str, Any]] = field(default_factory=list)
    _completion_state: str = "running"

    def __post_init__(self):
        if not self.state_history:
            self.state_history.append({
                "state": self.current_state,
                "timestamp": self.updated_at
            })

    def transition_to(self, target_state: str) -> None:
        if target_state == self.current_state:
            return  # Idempotent transition to same state
        allowed = ALLOWED_STATE_TRANSITIONS.get(self.current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(self.current_state, target_state)
        
        self.current_state = target_state
        self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        self.state_history.append({
            "state": target_state,
            "timestamp": self.updated_at
        })
        
        # Keep completion_state in sync for backward compatibility
        if target_state == "COMPLETED":
            self._completion_state = "success"
        elif target_state in ("FAILED", "TIMEOUT"):
            self._completion_state = "error"
        elif target_state == "CANCELLED":
            self._completion_state = "cancelled"
        elif target_state == "WAITING_PERMISSION":
            self._completion_state = "pending_permission"

    @property
    def completion_state(self) -> str:
        return self._completion_state

    @completion_state.setter
    def completion_state(self, val: str) -> None:
        self._completion_state = val
        if val == "cancelled" and self.current_state != "CANCELLED":
            try:
                self.transition_to("CANCELLED")
            except InvalidStateTransitionError:
                self.current_state = "CANCELLED"
        elif val == "error" and self.current_state not in ("FAILED", "TIMEOUT"):
            try:
                self.transition_to("FAILED")
            except InvalidStateTransitionError:
                self.current_state = "FAILED"
        elif val == "pending_permission" and self.current_state != "WAITING_PERMISSION":
            try:
                self.transition_to("WAITING_PERMISSION")
            except InvalidStateTransitionError:
                self.current_state = "WAITING_PERMISSION"
        elif val == "success" and self.current_state != "COMPLETED":
            try:
                self.transition_to("COMPLETED")
            except InvalidStateTransitionError:
                self.current_state = "COMPLETED"



class AgentCore:
    def __init__(self):
        self._model = None
        try:
            self._model = ModelFactory.get_provider()
        except Exception:
            self._model = None
        self.memory = SQLiteMemoryProvider(settings.DATABASE_PATH)
        self.tools = ToolRegistry()
        
        # Active task and cancellation registry
        self._active_tasks: Dict[str, Any] = {}
        self._canceled_sessions: set[str] = set()
        
        # Register tools
        self.tools.register(FileListTool())
        self.tools.register(FileReadTool())
        self.tools.register(FileSearchTool())
        self.tools.register(SystemInfoTool())
        self.tools.register(TerminalTool())
        self.tools.register(SuggestMemoryTool())
        
        self.security_manager = SecurityManager(PermissionLevel.USER_CONFIRMATION)
        
        # Initialize Tool Executor
        log_path = os.path.join(settings.SAARTHI_DATA_DIR, "logs", "tools.log")
        self.executor = ToolExecutor(
            registry=self.tools,
            security_manager=self.security_manager,
            allowed_roots=settings.ALLOWED_ROOTS,
            log_path=log_path
        )

    @property
    def model(self):
        if self._model is None:
            self._model = ModelFactory.get_provider()
        return self._model

    @model.setter
    def model(self, val):
        self._model = val

    @model.deleter
    def model(self):
        self._model = None

    def cancel_session(self, session_id: str) -> bool:
        import asyncio
        self._canceled_sessions.add(session_id)
        task = self._active_tasks.get(session_id)
        if task and not task.done():
            if task != asyncio.current_task():
                task.cancel()
            return True
        return False

    def _route_tools(self, user_query: str, history: list) -> set[str]:
        query_lower = user_query.lower()
        
        # Define keyword groups
        file_keywords = {
            "list", "files", "directories", "workspace", "folder", "ls", "dir", 
            "read", "cat", "view", "show content", "open file", "file_read", 
            "search", "grep", "find in file", "find string", "file_search", 
            "pdf", "txt", "log", "csv", "path", "filepath"
        }
        system_keywords = {"system", "specs", "host", "os", "hardware", "cpu", "ram", "system_info", "gpu", "nvidia-smi"}
        command_keywords = {"run", "execute", "cmd", "powershell", "shell", "terminal", "pytest", "command", "pip", "python", "npm"}
        memory_keywords = {"remember", "forget", "memory", "memories", "preference", "preferences", "located", "prefer"}
        
        relevant = set()
        if any(kw in query_lower for kw in file_keywords):
            relevant.update(["file_list", "file_read", "file_search"])
        if any(kw in query_lower for kw in system_keywords):
            relevant.add("system_info")
        if any(kw in query_lower for kw in command_keywords):
            relevant.add("terminal")
        if any(kw in query_lower for kw in memory_keywords):
            relevant.add("suggest_memory")
            
        # Fallback 1: Add any tools that were already called in the history of the current loop
        for msg in reversed(history[-10:]):
            try:
                data = json.loads(msg.get("message", ""))
                if isinstance(data, dict):
                    if data.get("type") in ("tool_call", "tool_result", "permission_request"):
                        t_name = data.get("tool")
                        if t_name:
                            relevant.add(t_name)
            except Exception:
                pass

        # Fallback 2: Check for general question keywords (if matched, we do NOT add any fallback tools)
        is_general_question = any(q in query_lower for q in [
            "what is the capital", "who is", "why is", "tell me a joke", "how many", 
            "what is the date", "what is your name", "who are you", "what is the height"
        ])
        
        # Fallback 3: If it's not a clear general question, and no tools are matched, we include all non-privileged tools as a fallback
        if not relevant and not is_general_question:
            action_verbs = {"find", "search", "run", "show", "get", "check", "inspect", "do", "perform", "list"}
            if any(w in query_lower for w in action_verbs) or len(query_lower.split()) > 3:
                relevant.update(["file_list", "file_read", "file_search", "system_info", "suggest_memory"])
                
        return relevant

    def _get_relevant_memories(self, user_query: str) -> list[dict]:
        user_query_lower = user_query.lower()
        
        # 1. Keyword extraction (ignoring stop words)
        stop_words = {
            "what", "who", "why", "how", "where", "when", "which", "is", "the", "a", "an",
            "of", "in", "to", "for", "with", "on", "at", "by", "from", "about", "me", "you",
            "my", "your", "that", "this", "these", "those", "it", "they", "them", "he", "she"
        }
        words = re.findall(r"\b\w{3,}\b", user_query_lower)
        keywords = [w for w in words if w not in stop_words]
        
        # Fetch candidate memories from SQLite using keywords
        candidates = {}
        for kw in keywords:
            search_res = memory_manager.search_memory(kw)
            for mem in search_res:
                candidates[mem["id"]] = mem
                
        # If no keywords matched, list all active memories to see if any match the query
        if not candidates:
            all_mems = memory_manager.list_memories(status="ACTIVE")
            for mem in all_mems:
                if mem["key"].lower() in user_query_lower or mem["content"].lower() in user_query_lower:
                    candidates[mem["id"]] = mem
                    
        # 2. Score and Rank
        scored_mems = []
        project_id = os.path.basename(settings.TOOL_ROOT_PATH).lower()
        
        for mem in candidates.values():
            mem_project = mem.get("project_id")
            # If memory belongs to a different project, skip it
            if mem_project and mem_project.lower() != project_id:
                continue
                
            score = 0
            mem_content_lower = mem["content"].lower()
            mem_key_lower = mem["key"].lower()
            
            # Key match
            if mem_key_lower in user_query_lower:
                score += 10
            # Content match
            if mem_content_lower in user_query_lower:
                score += 5
                
            # Keyword matches
            for kw in keywords:
                if kw in mem_content_lower:
                    score += 2
                if kw in mem_key_lower:
                    score += 3
                    
            # Category boost based on query context
            category = mem["category"].upper()
            if category in ("USER", "PREFERENCE") and any(k in user_query_lower for k in ["prefer", "user", "me", "my", "personal", "like"]):
                score += 5
            elif category == "PROJECT" and any(k in user_query_lower for k in ["project", "code", "located", "source", "path", "saarthi"]):
                score += 5
            elif category in ("FACT", "INSTRUCTION", "WORKFLOW") and any(k in user_query_lower for k in ["fact", "know", "rule", "instruction", "workflow"]):
                score += 5
                
            # Read confidence from metadata if present
            confidence = mem.get("metadata", {}).get("confidence", 1.0)
            score += int(confidence * 5)
            
            if score > 0:
                scored_mems.append((score, mem))
                
        # Rank by score descending
        scored_mems.sort(key=lambda x: x[0], reverse=True)
        top_mems = [mem for score, mem in scored_mems[:settings.MAX_MEMORY_RESULTS]]
        
        # 3. Fit in context limits
        result = []
        current_chars = 0
        for mem in top_mems:
            mem_str = f"- {mem['content']}"
            if current_chars + len(mem_str) <= settings.MAX_MEMORY_CONTEXT_CHARS:
                result.append(mem)
                current_chars += len(mem_str)
            else:
                break
                
        # Update last_accessed_at for retrieved memories
        for mem in result:
            try:
                memory_manager.update_memory(mem["id"], last_accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"))
            except Exception:
                pass
                
        return result

    def _get_system_prompt(self, session_id: str, history: list, relevant_tools: set[str], retrieved_memories: list[dict]) -> str:
        # 1. Available Tools Compact Manifest
        compact_tools = []
        for name, info in self.tools.list_tools().items():
            desc = info['description']
            if len(desc) > 100:
                desc = desc[:97] + "..."
            compact_tools.append(f"- {name}: {desc}")
        compact_tools_str = "\n".join(compact_tools)
        
        # 2. Detailed schema for relevant tools only
        detailed_schemas = []
        for name in relevant_tools:
            info = self.tools.get(name)
            if info:
                schema_str = json.dumps(info.input_schema)
                if len(schema_str) > settings.MAX_TOOL_DESCRIPTION_CHARS:
                    schema_str = schema_str[:settings.MAX_TOOL_DESCRIPTION_CHARS] + "..."
                detailed_schemas.append(
                    f"Tool '{name}' detailed argument schema:\n"
                    f"Input Schema: {schema_str}"
                )
        detailed_schemas_str = "\n\n".join(detailed_schemas)
        
        # 3. Format active memories (relevance matched)
        project_id = os.path.basename(settings.TOOL_ROOT_PATH)
        memories_ctx = ""
        if retrieved_memories:
            mems_by_cat = {}
            for m in retrieved_memories:
                cat = m["category"]
                mems_by_cat.setdefault(cat, []).append(m)
                
            mem_parts = []
            for cat, mems in mems_by_cat.items():
                header = f"{cat} MEMORY:" if cat != "PROJECT" else f"PROJECT MEMORY ({project_id}):"
                mem_parts.append(f"{header}\n" + "\n".join(f"- {m['content']}" for m in mems))
                
            if mem_parts:
                memories_ctx = "\n\n=== PERSISTENT MEMORIES ===\n" + "\n\n".join(mem_parts) + "\n===========================\n"

        # 4. Build Compact System Prompt with Personality
        system_prompt = (
            "You are Saarthi, a calm, intelligent, and practical personal AI assistant.\n"
            "Identity: Assistant for safe Windows workstation tasks.\n"
            "Response Behavior:\n"
            "- Be concise, professional, and helpful.\n"
            "- Proactively offer suggestions when useful, but do not be verbose.\n"
            "- Be honest about limitations and do not claim to know things outside context.\n"
            "- Keep responses clean: do not output <think>, <thinking>, or 'Thinking...' blocks.\n"
            "- Never expose raw tool-call syntax to the user outside the protocol.\n\n"
        )
        
        if relevant_tools:
            system_prompt += f"Available Tools:\n{compact_tools_str}\n\n"
            if detailed_schemas_str:
                system_prompt += (
                    f"### DETAILED ARGUMENT SCHEMA FOR RELEVANT TOOLS ###\n"
                    f"{detailed_schemas_str}\n\n"
                )
            system_prompt += (
                "Tool Call Protocol: If you need to call a tool, output exactly:\n"
                "[TOOL_CALL]\n"
                '{"tool": "tool_name", "arguments": {...}}\n'
                "[/TOOL_CALL]\n"
                "Write a brief explanation first, then the block. Never guess tool outputs.\n\n"
            )
        else:
            system_prompt += (
                "You do not have access to any tools for this request. Please answer the user directly based on your knowledge and context.\n\n"
            )
            
        system_prompt += (
            "Memory handling: Propose saving details by calling the `suggest_memory` tool when the user shares stable preferences, projects, workflows, or important facts.\n"
            "Safety: The backend enforces permissions and trusted paths. Never assume a tool succeeded until a result is returned."
            f"{memories_ctx}"
        )
        return system_prompt

    def _log_diagnostics(self, diag: dict) -> None:
        log_dir = os.path.join(settings.SAARTHI_DATA_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "agent_diagnostics.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(diag) + "\n")
        except Exception as e:
            print(f"Warning: Failed to write agent diagnostics log: {str(e)}")

    async def handle_message(self, session_id: str, user_message: str) -> str:
        if session_id in self._canceled_sessions and session_id not in self._active_tasks:
            cancel_msg = "Task execution was cancelled by the user."
            cancel_json = json.dumps({"type": "text", "content": cancel_msg})
            await self.memory.add_message(session_id, "assistant", cancel_json)
            self._canceled_sessions.discard(session_id)
            return cancel_json

        self._canceled_sessions.discard(session_id)
        try:
            import asyncio
            current_task = asyncio.current_task()
            if current_task:
                self._active_tasks[session_id] = current_task
        except Exception:
            pass

        request_id = f"req-{uuid.uuid4().hex[:8]}"
        state = AgentState(
            session_id=session_id,
            request_id=request_id,
            user_request=user_message
        )
        
        try:
            # Check if this is an explicit memory command
            cmd_response = await MemoryCommandProcessor.process(user_message, session_id)
            if cmd_response is not None:
                user_json = json.dumps({"type": "text", "content": user_message})
                await self.memory.add_message(session_id, "user", user_json)
                
                assistant_json = json.dumps({"type": "text", "content": cmd_response})
                await self.memory.add_message(session_id, "assistant", assistant_json)
                
                duration = time.perf_counter() - state.start_time
                self._log_diagnostics({
                    "request_id": request_id,
                    "session_id": session_id,
                    "model": self.model.model_name,
                    "prompt_token_estimate": len(user_message) // 4,
                    "selected_tools": [],
                    "tool_execution_duration": 0.0,
                    "model_duration": 0.0,
                    "total_duration": duration,
                    "iteration_count": 0,
                    "error_status": False
                })
                return assistant_json

            # Save user message to memory as structured JSON
            user_json = json.dumps({"type": "text", "content": user_message})
            await self.memory.add_message(session_id, "user", user_json)

            # Run the agent loop
            return await self._run_agent_loop(state)
        except MemoryApprovalRequiredException as mae:
            user_json = json.dumps({"type": "text", "content": user_message})
            await self.memory.add_message(session_id, "user", user_json)
            
            req = mae.memory_request
            req_json = json.dumps({
                "type": "memory_request",
                "request_id": req.request_id,
                "category": req.category,
                "key": req.key,
                "content": req.content,
                "project_id": req.project_id,
                "question": req.question,
                "status": req.status,
                "session_id": req.session_id,
                "action": req.action
            })
            await self.memory.add_message(session_id, "assistant", req_json)
            
            duration = time.perf_counter() - state.start_time
            self._log_diagnostics({
                "request_id": request_id,
                "session_id": session_id,
                "model": self.model.model_name,
                "prompt_token_estimate": len(user_message) // 4,
                "selected_tools": [],
                "tool_execution_duration": 0.0,
                "model_duration": 0.0,
                "total_duration": duration,
                "iteration_count": 0,
                "error_status": False
            })
            raise mae
        except asyncio.CancelledError:
            try:
                cur_t = asyncio.current_task()
                if cur_t and hasattr(cur_t, "uncancel"):
                    cur_t.uncancel()
            except Exception:
                pass
            state.completion_state = "cancelled"
            cancel_msg = "Task execution was cancelled by the user."
            cancel_json = json.dumps({"type": "text", "content": cancel_msg})
            await self.memory.add_message(session_id, "assistant", cancel_json)
            return cancel_json
        finally:
            self._active_tasks.pop(session_id, None)

    async def resume_with_permission(self, req: PermissionRequest, approved: bool) -> str:
        session_id = req.session_id
        tool_name = req.tool_name
        tool_args = req.arguments

        self._canceled_sessions.discard(session_id)
        try:
            import asyncio
            current_task = asyncio.current_task()
            if current_task:
                self._active_tasks[session_id] = current_task
        except Exception:
            pass

        request_id = f"req-{uuid.uuid4().hex[:8]}"
        state = AgentState(
            session_id=session_id,
            request_id=request_id,
            user_request=f"Resume execution of {tool_name}"
        )
        
        try:
            # Soft update status of request card in history
            history = await self.memory.get_messages(session_id)
            for i, msg in enumerate(reversed(history)):
                try:
                    data = json.loads(msg.get("message", ""))
                    if data.get("type") == "permission_request" and data.get("request_id") == req.request_id:
                        data["status"] = "approved" if approved else "denied"
                        break
                except Exception:
                    continue

            if approved:
                try:
                    tool_args["session_id"] = session_id
                    tool_result = await self.executor.execute_tool(
                        name=tool_name,
                        arguments=tool_args,
                        session_id=session_id,
                        confirmed=True
                    )
                    await self.memory.add_message(
                        session_id,
                        "user",
                        json.dumps({
                            "type": "tool_result",
                            "tool": tool_name,
                            "success": tool_result.get("success", False),
                            "result": tool_result.get("data"),
                            "error": tool_result.get("error")
                        })
                    )
                except MemoryApprovalRequiredException as mae:
                    req_mem = mae.memory_request
                    req_json = json.dumps({
                        "type": "memory_request",
                        "request_id": req_mem.request_id,
                        "category": req_mem.category,
                        "key": req_mem.key,
                        "content": req_mem.content,
                        "project_id": req_mem.project_id,
                        "question": req_mem.question,
                        "status": req_mem.status,
                        "session_id": req_mem.session_id
                    })
                    await self.memory.add_message(session_id, "assistant", req_json)
                    raise mae
                except Exception as e:
                    error_msg = f"Failed to execute tool call: {str(e)}"
                    await self.memory.add_message(
                        session_id,
                        "user",
                        json.dumps({
                            "type": "tool_result",
                            "tool": tool_name,
                            "success": False,
                            "error": {
                                "type": "EXECUTION_ERROR",
                                "message": error_msg
                            }
                        })
                    )
            else:
                await self.memory.add_message(
                    session_id,
                    "user",
                    json.dumps({
                        "type": "tool_result",
                        "tool": tool_name,
                        "success": False,
                        "error": {
                            "type": "PERMISSION_DENIED",
                            "message": "Execution Denied by User."
                        }
                    })
                )

            return await self._run_agent_loop(state)
        finally:
            self._active_tasks.pop(session_id, None)

    async def resume_with_memory_approval(self, req: MemoryRequest, approved: bool) -> str:
        session_id = req.session_id
        
        # Soft update status of request card in history
        history = await self.memory.get_messages(session_id)
        for i, msg in enumerate(reversed(history)):
            try:
                data = json.loads(msg.get("message", ""))
                if data.get("type") == "memory_request" and data.get("request_id") == req.request_id:
                    data["status"] = "approved" if approved else "denied"
                    break
            except Exception:
                continue

        if approved:
            if req.action == "delete":
                mems = memory_manager.list_memories(status="ACTIVE")
                deleted_count = 0
                for mem in mems:
                    if req.key == "forget_project":
                        if mem.get("project_id") and mem["project_id"].lower() == req.project_id.lower():
                            memory_manager.delete_memory(mem["id"])
                            deleted_count += 1
                    else:
                        if (req.category == mem["category"] and req.content.lower() in mem["content"].lower()) or \
                           (req.key == mem["key"] and req.category == mem["category"]):
                            memory_manager.delete_memory(mem["id"])
                            deleted_count += 1
                resp_content = f"I have forgotten that information (removed {deleted_count} memories)."
            else:
                metadata = {"confidence": 1.0}
                memory_manager.create_memory(
                    category=req.category,
                    key=req.key,
                    content=req.content,
                    project_id=req.project_id,
                    source="user",
                    metadata=metadata
                )
                resp_content = f"I have successfully stored this in my {req.category} memory: '{req.content}'."
        else:
            if req.action == "delete":
                resp_content = f"Understood, I will keep that information."
            else:
                resp_content = f"Understood, I will not remember that."

        assistant_json = json.dumps({"type": "text", "content": resp_content})
        await self.memory.add_message(session_id, "assistant", assistant_json)
        return assistant_json

    async def _run_agent_loop(self, state: AgentState) -> str:
        max_iterations = getattr(settings, "MAX_AGENT_ITERATIONS", 6)
        session_id = state.session_id
        import asyncio
        
        total_model_duration = 0.0
        total_tool_duration = 0.0
        
        open_tag_re = re.compile(r"\[\s*TOOL_?(\w+)\s*\]", re.IGNORECASE)
        close_tag_re = re.compile(r"\[\s*/\s*TOOL_?(\w+)\s*\]", re.IGNORECASE)
        
        latest_user_msg = state.user_request
        state.retrieved_memories = self._get_relevant_memories(latest_user_msg)
        state.transition_to("RUNNING")
        
        while state.iteration < max_iterations:
            if session_id in self._canceled_sessions:
                state.transition_to("CANCELLED")
                cancel_msg = "Task execution was cancelled by the user."
                cancel_json = json.dumps({"type": "text", "content": cancel_msg})
                await self.memory.add_message(session_id, "assistant", cancel_json)
                self._log_diagnostics({
                    "request_id": state.request_id,
                    "session_id": session_id,
                    "model": self.model.model_name,
                    "prompt_token_estimate": len(latest_user_msg) // 4,
                    "selected_tools": list(state.called_tools),
                    "tool_execution_duration": total_tool_duration,
                    "model_duration": total_model_duration,
                    "total_duration": time.perf_counter() - state.start_time,
                    "iteration_count": state.iteration,
                    "error_status": True
                })
                return cancel_json

            state.transition_to("RUNNING")
            state.iteration += 1
            
            history = await self.memory.get_messages(session_id)
            
            formatted_history = []
            for msg in history:
                sender = msg.get("sender")
                raw_text = msg.get("message", "")
                
                try:
                    data = json.loads(raw_text)
                    if isinstance(data, dict) and "type" in data:
                        t = data["type"]
                        if t == "text":
                            content = data["content"]
                        elif t == "tool_call":
                            content = f"[TOOL_CALL]\n{{\n  \"tool\": \"{data['tool']}\",\n  \"arguments\": {json.dumps(data['arguments'])}\n}}\n[/TOOL_CALL]"
                        elif t == "tool_result":
                            result_data = {
                                "tool": data["tool"],
                                "success": data["success"]
                            }
                            if data["success"]:
                                result_data["result"] = data["result"]
                            else:
                                result_data["error"] = data["error"]
                            content = json.dumps(result_data, indent=2)
                        elif t == "permission_request":
                            content = f"[Permission Request for {data['tool']} - Status: {data['status']}]"
                        elif t == "memory_request":
                            content = f"[Memory Request for category {data['category']} - Status: {data['status']}]"
                        else:
                            content = raw_text
                    else:
                        content = raw_text
                except Exception:
                    content = raw_text
                
                formatted_history.append({"sender": sender, "message": content})
                
            relevant_tools = self._route_tools(latest_user_msg, history)
            relevant_tools.update(state.called_tools)
            
            system_prompt = self._get_system_prompt(session_id, history, relevant_tools, state.retrieved_memories)
            
            model_start = time.perf_counter()
            try:
                if session_id in self._canceled_sessions:
                    raise asyncio.CancelledError()
                state.transition_to("WAITING_MODEL")
                response = await self.model.generate_response(
                    prompt="Analyze the tool result and continue or provide final response.",
                    history=formatted_history,
                    system_prompt=system_prompt
                )
            except asyncio.CancelledError:
                try:
                    cur_t = asyncio.current_task()
                    if cur_t and hasattr(cur_t, "uncancel"):
                        cur_t.uncancel()
                except Exception:
                    pass
                state.transition_to("CANCELLED")
                cancel_msg = "Task execution was cancelled by the user."
                cancel_json = json.dumps({"type": "text", "content": cancel_msg})
                await self.memory.add_message(session_id, "assistant", cancel_json)
                return cancel_json
            except Exception as e:
                error_msg = f"I encountered an error communicating with the local AI model: {str(e)}"
                state.errors.append(str(e))
                state.transition_to("FAILED")
                
                err_json = json.dumps({"type": "text", "content": error_msg})
                await self.memory.add_message(session_id, "assistant", err_json)
                
                self._log_diagnostics({
                    "request_id": state.request_id,
                    "session_id": session_id,
                    "model": self.model.model_name,
                    "prompt_token_estimate": len(latest_user_msg) // 4,
                    "selected_tools": list(state.called_tools),
                    "tool_execution_duration": total_tool_duration,
                    "model_duration": total_model_duration,
                    "total_duration": time.perf_counter() - state.start_time,
                    "iteration_count": state.iteration,
                    "error_status": True
                })
                return err_json
                
            total_model_duration += (time.perf_counter() - model_start)
            
            from app.models.ollama import clean_reasoning
            response = clean_reasoning(response)
            
            open_matches = list(open_tag_re.finditer(response))
            close_matches = list(close_tag_re.finditer(response))
            has_tool_call = len(open_matches) > 0 or len(close_matches) > 0
            
            if has_tool_call:
                state.transition_to("WAITING_TOOL")
                if session_id in self._canceled_sessions:
                    state.transition_to("CANCELLED")
                    cancel_msg = "Task execution was cancelled by the user."
                    cancel_json = json.dumps({"type": "text", "content": cancel_msg})
                    await self.memory.add_message(session_id, "assistant", cancel_json)
                    return cancel_json

                tool_calls_to_process = []
                malformed_error = None

                if len(open_matches) != len(close_matches):
                    malformed_error = "Malformed tool call: Must contain matching opening and closing tool tags."
                else:
                    for idx in range(len(open_matches)):
                        open_match = open_matches[idx]
                        close_match = close_matches[idx]

                        if open_match.start() >= close_match.start():
                            malformed_error = "Malformed tool call: Tag pairs are out of order."
                            break

                        open_tag_type = open_match.group(1).upper()
                        close_tag_type = close_match.group(1).upper()

                        if open_tag_type != close_tag_type:
                            malformed_error = f"Mismatched tags: Opened [TOOL_{open_tag_type}] but closed [/TOOL_{close_tag_type}]."
                            break

                        start_idx = open_match.end()
                        end_idx = close_match.start()
                        json_str = response[start_idx:end_idx].strip()

                        intro_text = response[:open_matches[0].start()].strip() if idx == 0 else ""
                        if not intro_text:
                            intro_text = "Processing tool request..."
                        intro_text = clean_reasoning(intro_text)

                        tool_name = None
                        tool_args = {}
                        is_valid = False
                        error_msg = None

                        try:
                            call_data = json.loads(json_str)
                            if not isinstance(call_data, dict):
                                error_msg = "Malformed tool call: JSON must be an object."
                            else:
                                if open_tag_type == "CALL":
                                    tool_name = call_data.get("tool")
                                    tool_args = call_data.get("arguments", {})
                                else:
                                    tool_name = open_tag_type.lower()
                                    if "arguments" in call_data:
                                        tool_args = call_data.get("arguments", {})
                                    else:
                                        tool_args = call_data
                                if not isinstance(tool_args, dict):
                                    tool_args = {}

                                if not tool_name:
                                    error_msg = "Malformed tool call: Tool name is missing."
                                else:
                                    tool = self.tools.get(tool_name)
                                    if not tool:
                                        error_msg = f"UNKNOWN_TOOL: Tool '{tool_name}' is not registered."
                                    else:
                                        try:
                                            validate_arguments(tool.input_schema, tool_args)
                                            is_valid = True
                                        except ValueError as ve:
                                            error_msg = f"INVALID_ARGUMENT: {str(ve)}"
                        except Exception as je:
                            error_msg = f"Malformed tool call: Failed to parse JSON. Details: {str(je)}"

                        tool_calls_to_process.append({
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "is_valid": is_valid,
                            "error_msg": error_msg,
                            "intro_text": intro_text
                        })

                if malformed_error or not tool_calls_to_process:
                    call_json = json.dumps({
                        "type": "tool_call",
                        "tool": "unknown",
                        "arguments": {},
                        "intro": "Attempting to call a tool..."
                    })
                    await self.memory.add_message(session_id, "assistant", call_json)

                    err_res = {
                        "type": "tool_result",
                        "tool": "unknown",
                        "success": False,
                        "error": {
                            "type": "MALFORMED_TOOL_CALL",
                            "message": malformed_error or "Malformed tool call: Unable to process tag blocks."
                        }
                    }
                    await self.memory.add_message(session_id, "user", json.dumps(err_res))
                    state.tool_results.append(err_res)
                    continue

                for call_info in tool_calls_to_process:
                    if session_id in self._canceled_sessions:
                        state.completion_state = "cancelled"
                        cancel_msg = "Task execution was cancelled by the user."
                        cancel_json = json.dumps({"type": "text", "content": cancel_msg})
                        await self.memory.add_message(session_id, "assistant", cancel_json)
                        return cancel_json

                    tool_name = call_info["tool_name"]
                    tool_args = call_info["tool_args"]
                    is_valid = call_info["is_valid"]
                    error_msg = call_info["error_msg"]
                    intro_text = call_info["intro_text"]

                    state.selected_tool = tool_name
                    if tool_name:
                        state.called_tools.append(tool_name)

                    if is_valid:
                        tool = self.tools.get(tool_name)
                        required_level = tool.permission_level

                        call_json = json.dumps({
                            "type": "tool_call",
                            "tool": tool_name,
                            "arguments": tool_args,
                            "intro": intro_text
                        })
                        await self.memory.add_message(session_id, "assistant", call_json)

                        if required_level == PermissionLevel.PRIVILEGED:
                            err_res = {
                                "type": "tool_result",
                                "tool": tool_name,
                                "success": False,
                                "error": {
                                    "type": "PERMISSION_DENIED",
                                    "message": f"Tool '{tool_name}' requires PRIVILEGED safety level which is rejected."
                                }
                            }
                            await self.memory.add_message(session_id, "user", json.dumps(err_res))
                            state.tool_results.append(err_res)
                            continue

                        if required_level == PermissionLevel.USER_CONFIRMATION:
                            from app.security.permissions import permission_store
                            req = permission_store.create_request(
                                tool_name=tool_name,
                                arguments=tool_args,
                                permission_level=required_level.value,
                                risk_level=tool.risk_classification,
                                session_id=session_id
                            )

                            req_json = json.dumps({
                                "type": "permission_request",
                                "request_id": req.request_id,
                                "tool": req.tool_name,
                                "action_description": req.action_description,
                                "arguments": req.arguments,
                                "permission_level": req.permission_level,
                                "risk_level": req.risk_level,
                                "status": req.status,
                                "session_id": req.session_id
                            })
                            await self.memory.add_message(session_id, "assistant", req_json)
                            state.completion_state = "pending_permission"
                            state.pending_permission = req.to_dict()

                            self._log_diagnostics({
                                "request_id": state.request_id,
                                "session_id": session_id,
                                "model": self.model.model_name,
                                "prompt_token_estimate": len(latest_user_msg) // 4,
                                "selected_tools": list(state.called_tools),
                                "tool_execution_duration": total_tool_duration,
                                "model_duration": total_model_duration,
                                "total_duration": time.perf_counter() - state.start_time,
                                "iteration_count": state.iteration,
                                "error_status": False
                            })
                            raise PermissionRequiredException(req)

                        tool_args["session_id"] = session_id
                        tool_start = time.perf_counter()
                        try:
                            if session_id in self._canceled_sessions:
                                raise asyncio.CancelledError()
                            state.transition_to("EXECUTING_TOOL")
                            tool_result = await self.executor.execute_tool(
                                name=tool_name,
                                arguments=tool_args,
                                session_id=session_id,
                                confirmed=True
                            )
                            total_tool_duration += (time.perf_counter() - tool_start)
                        except asyncio.CancelledError:
                            try:
                                cur_t = asyncio.current_task()
                                if cur_t and hasattr(cur_t, "uncancel"):
                                    cur_t.uncancel()
                            except Exception:
                                pass
                            state.transition_to("CANCELLED")
                            cancel_msg = "Task execution was cancelled by the user."
                            cancel_json = json.dumps({"type": "text", "content": cancel_msg})
                            await self.memory.add_message(session_id, "assistant", cancel_json)
                            return cancel_json
                        except MemoryApprovalRequiredException as mae:
                            req = mae.memory_request
                            req_json = json.dumps({
                                "type": "memory_request",
                                "request_id": req.request_id,
                                "category": req.category,
                                "key": req.key,
                                "content": req.content,
                                "project_id": req.project_id,
                                "question": req.question,
                                "status": req.status,
                                "session_id": req.session_id,
                                "action": req.action
                            })
                            await self.memory.add_message(session_id, "assistant", req_json)
                            state.completion_state = "pending_memory"

                            self._log_diagnostics({
                                "request_id": state.request_id,
                                "session_id": session_id,
                                "model": self.model.model_name,
                                "prompt_token_estimate": len(latest_user_msg) // 4,
                                "selected_tools": list(state.called_tools),
                                "tool_execution_duration": total_tool_duration,
                                "model_duration": total_model_duration,
                                "total_duration": time.perf_counter() - state.start_time,
                                "iteration_count": state.iteration,
                                "error_status": False
                            })
                            raise mae
                        except Exception as e:
                            total_tool_duration += (time.perf_counter() - tool_start)
                            tool_result = {
                                "success": False,
                                "tool": tool_name,
                                "error": {
                                    "code": "EXECUTION_ERROR",
                                    "message": str(e)
                                }
                            }

                        res_json = json.dumps({
                            "type": "tool_result",
                            "tool": tool_name,
                            "success": tool_result.get("success", False),
                            "result": tool_result.get("data"),
                            "error": tool_result.get("error")
                        })
                        await self.memory.add_message(session_id, "user", res_json)
                        state.tool_results.append(tool_result)
                        state.transition_to("RUNNING")
                    else:
                        call_json = json.dumps({
                            "type": "tool_call",
                            "tool": tool_name or "unknown",
                            "arguments": tool_args or {},
                            "intro": intro_text
                        })
                        await self.memory.add_message(session_id, "assistant", call_json)

                        err_type = "MALFORMED_TOOL_CALL"
                        if error_msg and "UNKNOWN_TOOL" in error_msg:
                            err_type = "UNKNOWN_TOOL"
                        elif error_msg and "INVALID_ARGUMENT" in error_msg:
                            err_type = "INVALID_ARGUMENT"

                        err_res = {
                            "type": "tool_result",
                            "tool": tool_name or "unknown",
                            "success": False,
                            "error": {
                                "type": err_type,
                                "message": error_msg
                            }
                        }
                        await self.memory.add_message(session_id, "user", json.dumps(err_res))
                        state.tool_results.append(err_res)
                        state.transition_to("RUNNING")
            else:
                clean_response = open_tag_re.sub("", response)
                clean_response = close_tag_re.sub("", clean_response).strip()
                clean_response = clean_reasoning(clean_response)
                
                text_json = json.dumps({"type": "text", "content": clean_response})
                await self.memory.add_message(session_id, "assistant", text_json)
                state.completion_state = "success"
                
                self._log_diagnostics({
                    "request_id": state.request_id,
                    "session_id": session_id,
                    "model": self.model.model_name,
                    "prompt_token_estimate": len(latest_user_msg) // 4,
                    "selected_tools": list(state.called_tools),
                    "tool_execution_duration": total_tool_duration,
                    "model_duration": total_model_duration,
                    "total_duration": time.perf_counter() - state.start_time,
                    "iteration_count": state.iteration,
                    "error_status": False
                })
                return text_json
                
        limit_msg = f"Task was stopped because the maximum tool iteration limit of {max_iterations} was reached."
        limit_json = json.dumps({"type": "text", "content": limit_msg})
        await self.memory.add_message(session_id, "assistant", limit_json)
        state.completion_state = "error"
        state.errors.append("Max iterations reached")
        
        self._log_diagnostics({
            "request_id": state.request_id,
            "session_id": session_id,
            "model": self.model.model_name,
            "prompt_token_estimate": len(latest_user_msg) // 4,
            "selected_tools": list(state.called_tools),
            "tool_execution_duration": total_tool_duration,
            "model_duration": total_model_duration,
            "total_duration": time.perf_counter() - state.start_time,
            "iteration_count": state.iteration,
            "error_status": True
        })
        return limit_json
