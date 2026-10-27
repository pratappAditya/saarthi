import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.intelligence.memory.memory_models import (
    MemoryItem, MemoryClass, MemoryType, MemoryScope, MemoryProvenance, RetentionState
)
from app.intelligence.memory.memory_store import MemoryStore, memory_store
from app.intelligence.memory.memory_retrieval import MemoryRetriever

logger = logging.getLogger("app.intelligence.memory_manager")

# Strict regex patterns for credentials and secrets that must NEVER be persisted to durable memory
SECRET_PATTERNS = [
    re.compile(r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*[^\s,;]{4,}"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|bearer)\s*[:=]\s*[^\s,;]{8,}"),
    re.compile(r"\b(?:sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{30,}|xox[baprs]-[a-zA-Z0-9]{10,})\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"),  # Credit card numbers
]


class MemoryManager:
    """
    Production Deep Memory & Personal Intelligence Manager for Saarthi 2.0.
    Enforces privacy, tenant isolation, strict provenance invariance, secret sanitization,
    and natural language memory commands.
    """
    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or memory_store
        self.retriever = MemoryRetriever(store=self.store)

    @staticmethod
    def contains_sensitive_credentials(text: str) -> bool:
        """Checks if text contains secrets, credentials, or private authentication tokens."""
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                return True
        return False

    def forget(self, memory_id: int, user_id: Optional[str] = None) -> bool:
        """Deletes a memory item permanently and invalidates caches."""
        return self.store.delete_memory(memory_id, user_id=user_id)

    def create_fact(
        self,
        content: str,
        source: MemoryProvenance = MemoryProvenance.USER_EXPLICIT,
        importance: int = 7,
        domain: str = "general",
        user_id: str = "default_local_user",
        scope: MemoryScope = MemoryScope.GLOBAL_USER,
        project_id: Optional[str] = None,
        retention_state: RetentionState = RetentionState.DURABLE,
        expires_at: Optional[str] = None
    ) -> MemoryItem:
        """Creates a fact in durable memory with strict secret screening."""
        if self.contains_sensitive_credentials(content):
            raise ValueError("Security Policy Violation: Memory content contains sensitive credentials, API keys, or secrets.")

        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.USER_MEMORY,
            content=content,
            provenance=source,
            importance=importance,
            domain=domain,
            scope=scope,
            project_id=project_id,
            retention_state=retention_state.value,
            expires_at=expires_at,
            confidence=1.0 if source == MemoryProvenance.USER_EXPLICIT else 0.8
        )
        return self.store.create_memory(item)

    def create_preference(
        self,
        content: str,
        importance: int = 8,
        user_id: str = "default_local_user",
        scope: MemoryScope = MemoryScope.GLOBAL_USER,
        project_id: Optional[str] = None,
        provenance: MemoryProvenance = MemoryProvenance.USER_EXPLICIT
    ) -> MemoryItem:
        if self.contains_sensitive_credentials(content):
            raise ValueError("Security Policy Violation: Preference contains sensitive credentials.")

        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.PREFERENCE_MEMORY,
            content=content,
            provenance=provenance,
            importance=importance,
            domain="general",
            scope=scope,
            project_id=project_id,
            confidence=1.0 if provenance == MemoryProvenance.USER_EXPLICIT else 0.75
        )
        return self.store.create_memory(item)

    def create_project_memory(
        self,
        project_id: str,
        content: str,
        user_id: str = "default_local_user",
        importance: int = 8,
        provenance: MemoryProvenance = MemoryProvenance.USER_EXPLICIT
    ) -> MemoryItem:
        """Stores project-specific conventions, architecture, or constraints under PROJECT scope."""
        if self.contains_sensitive_credentials(content):
            raise ValueError("Security Policy Violation: Project memory contains sensitive credentials.")

        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.PROJECT_MEMORY,
            content=content,
            provenance=provenance,
            importance=importance,
            scope=MemoryScope.PROJECT,
            project_id=project_id,
            domain="engineering",
            confidence=1.0 if provenance == MemoryProvenance.USER_EXPLICIT else 0.85
        )
        return self.store.create_memory(item)

    def create_goal_memory(
        self,
        goal_id: str,
        content: str,
        user_id: str = "default_local_user",
        importance: int = 8,
        project_id: Optional[str] = None
    ) -> MemoryItem:
        """Stores goal objectives, milestones, or decisions."""
        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.GOAL_MEMORY,
            content=content,
            provenance=MemoryProvenance.USER_EXPLICIT,
            importance=importance,
            scope=MemoryScope.GOAL,
            goal_id=goal_id,
            project_id=project_id
        )
        return self.store.create_memory(item)

    def create_workflow_memory(
        self,
        workflow_id: str,
        content: str,
        user_id: str = "default_local_user",
        provenance: MemoryProvenance = MemoryProvenance.OBSERVED
    ) -> MemoryItem:
        """Stores recognized recurring workflows."""
        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.WORKFLOW_MEMORY,
            content=content,
            provenance=provenance,
            importance=6,
            scope=MemoryScope.GLOBAL_USER,
            workflow_id=workflow_id,
            confidence=0.80
        )
        return self.store.create_memory(item)

    def create_voice_memory(
        self,
        content: str,
        user_id: str = "default_local_user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryItem:
        """Stores voice-specific pronunciation, speaking speed, or dictionary rules."""
        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.VOICE_MEMORY,
            content=content,
            provenance=MemoryProvenance.USER_EXPLICIT,
            importance=7,
            scope=MemoryScope.GLOBAL_USER,
            metadata=metadata or {}
        )
        return self.store.create_memory(item)

    def create_multimodal_memory(
        self,
        content: str,
        source_doc: str,
        user_id: str = "default_local_user",
        project_id: Optional[str] = None,
        confirmed_by_user: bool = False
    ) -> MemoryItem:
        """
        Creates memory from documents, screenshots, or images.
        Strict Provenance Invariance: Always SOURCE_DERIVED until explicitly confirmed by the user.
        """
        if self.contains_sensitive_credentials(content):
            raise ValueError("Security Policy Violation: Multimodal memory contains sensitive credentials.")

        prov = MemoryProvenance.USER_EXPLICIT if confirmed_by_user else MemoryProvenance.SOURCE_DERIVED
        item = MemoryItem(
            user_id=user_id,
            memory_class=MemoryClass.PROJECT_MEMORY if project_id else MemoryClass.USER_MEMORY,
            content=content,
            provenance=prov,
            confidence=1.0 if confirmed_by_user else 0.85,
            importance=7,
            scope=MemoryScope.PROJECT if project_id else MemoryScope.GLOBAL_USER,
            project_id=project_id,
            metadata={"source_document": source_doc, "user_confirmed": confirmed_by_user}
        )
        return self.store.create_memory(item)

    def correct_memory(
        self,
        memory_id: int,
        new_content: str,
        user_id: str = "default_local_user"
    ) -> Optional[MemoryItem]:
        """
        Corrects an existing memory:
        Updates content, elevates provenance to USER_EXPLICIT, and records audit trail.
        """
        if self.contains_sensitive_credentials(new_content):
            raise ValueError("Security Policy Violation: Corrected content contains sensitive credentials.")

        existing = self.store.get_memory(memory_id, user_id=user_id)
        if not existing:
            return None

        updated = self.store.update_memory(
            memory_id=memory_id,
            user_id=user_id,
            content=new_content,
            provenance=MemoryProvenance.USER_EXPLICIT.value,
            confidence=1.0
        )
        return updated

    def search_memories(
        self,
        query: str,
        domain: Optional[str] = None,
        domains: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        scope: Optional[str] = None,
        limit: int = 10,
        user_id: str = "default_local_user",
        task_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        target_domains = domains if domains else ([domain] if domain else [None])
        seen_ids = set()
        all_results = []

        for d in target_domains:
            results = self.retriever.search(
                query=query,
                user_id=user_id,
                domain=d,
                project_id=project_id,
                scope=scope,
                limit=limit,
                task_id=task_id
            )
            for item in results:
                if item.id not in seen_ids:
                    seen_ids.add(item.id)
                    all_results.append(item.model_dump())

        return all_results[:limit]

    def list_all_memories(
        self,
        user_id: str = "default_local_user",
        domain: Optional[str] = None,
        project_id: Optional[str] = None,
        scope: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        memories = self.store.list_memories(
            user_id=user_id,
            domain=domain,
            project_id=project_id,
            scope=scope,
            limit=250
        )
        return [item.model_dump() for item in memories]

    def remember(
        self,
        content: str,
        domain: str = "general",
        user_id: str = "default_local_user",
        project_id: Optional[str] = None,
        source: MemoryProvenance = MemoryProvenance.USER_EXPLICIT
    ) -> Dict[str, Any]:
        item = self.create_fact(
            content=content,
            source=source,
            domain=domain,
            user_id=user_id,
            project_id=project_id,
            scope=MemoryScope.PROJECT if project_id else MemoryScope.GLOBAL_USER
        )
        d = item.model_dump()
        d["source"] = d.get("provenance", source.value if hasattr(source, "value") else str(source))
        return d

    def forget_by_query(self, query: str, user_id: str = "default_local_user") -> int:
        memories = self.list_all_memories(user_id=user_id)
        count = 0
        q_lower = query.lower()
        for m in memories:
            if q_lower in m["content"].lower():
                if self.forget(m["id"], user_id=user_id):
                    count += 1
        return count

    def clear_project_memory(self, project_id: str, user_id: str = "default_local_user") -> int:
        return self.store.clear_project_memories(user_id=user_id, project_id=project_id)

    def what_saarthi_knows(
        self,
        user_id: str = "default_local_user",
        project_id: Optional[str] = None,
        scope: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive 'What Saarthi Knows' inspection audit:
        Returns transparent itemization of each memory with What, Why, Provenance, Scope,
        Confidence, and edit/delete permissions.
        """
        memories = self.store.list_memories(
            user_id=user_id,
            domain=domain,
            project_id=project_id,
            scope=scope,
            limit=300
        )

        audit_list = []
        for m in memories:
            prov_str = m.provenance.value if hasattr(m.provenance, 'value') else str(m.provenance)
            scope_str = m.scope.value if hasattr(m.scope, 'value') else str(m.scope)

            # Build explainable 'Why Saarthi knows this'
            if prov_str in ["USER_EXPLICIT", "user_explicit"]:
                why = "Explicitly provided by user in conversation or settings."
            elif prov_str in ["SOURCE_DERIVED", "uploaded_document"]:
                src_doc = m.metadata.get("source_document", "an uploaded document or screenshot")
                why = f"Extracted from {src_doc}. Pending explicit user confirmation."
            elif prov_str in ["OBSERVED", "tool_observation"]:
                why = "Observed from recurring tool interactions or application workflow."
            else:
                why = "Inferred from behavioral interaction patterns (confidence scored, reversible)."

            audit_list.append({
                "id": m.id,
                "what": m.content,
                "why": why,
                "source": prov_str,
                "scope": scope_str,
                "memory_class": m.memory_class.value if hasattr(m.memory_class, 'value') else str(m.memory_class),
                "confidence": m.confidence,
                "importance": m.importance,
                "domain": m.domain,
                "project_id": m.project_id,
                "goal_id": m.goal_id,
                "retention_state": m.retention_state,
                "expires_at": m.expires_at,
                "created_at": m.created_at,
                "updated_at": m.updated_at,
                "can_edit": True,
                "can_delete": True
            })

        return audit_list

    def process_memory_command(
        self,
        command_text: str,
        user_id: str = "default_local_user",
        project_id: Optional[str] = None,
        domain: str = "general"
    ) -> Optional[Dict[str, Any]]:
        """
        Processes natural language memory commands:
        - 'Remember that I prefer [X]'
        - 'Remember this project uses [X]'
        - 'Forget that' / 'Forget [X]'
        - 'Forget everything you know about this project'
        - 'What do you remember about me?'
        - 'What do you know about this project?'
        - 'The information you have about [X] is wrong'
        """
        text = command_text.strip()
        text_lower = text.lower()

        # 1. Clear project memory
        if "forget everything you know about this project" in text_lower or "forget all project memory" in text_lower:
            target_proj = project_id or "default_project"
            count = self.clear_project_memory(project_id=target_proj, user_id=user_id)
            return {
                "action": "clear_project_memory",
                "project_id": target_proj,
                "deleted_count": count,
                "response": f"Cleared all {count} memories remembered for project '{target_proj}'."
            }

        # 2. Forget command
        if text_lower.startswith("forget that") or text_lower.startswith("forget about ") or text_lower.startswith("forget "):
            # Extract target
            target = re.sub(r"(?i)^forget (?:that|about )?", "", text).strip()
            if not target or target.lower() == "that":
                # Forget most recent memory
                all_mems = self.store.list_memories(user_id=user_id, limit=1)
                if all_mems:
                    self.forget(all_mems[0].id, user_id=user_id)
                    return {
                        "action": "forget",
                        "deleted_count": 1,
                        "forgotten_content": all_mems[0].content,
                        "response": f"Forgotten: '{all_mems[0].content}'."
                    }
                return {"action": "forget", "deleted_count": 0, "response": "No memories found to forget."}
            else:
                count = self.forget_by_query(target, user_id=user_id)
                return {
                    "action": "forget",
                    "deleted_count": count,
                    "target": target,
                    "response": f"Removed {count} memory items matching '{target}'."
                }

        # 3. What do you remember about me / What do you know about me
        if "what do you remember about me" in text_lower or "what do you know about me" in text_lower:
            items = self.what_saarthi_knows(user_id=user_id, scope=MemoryScope.GLOBAL_USER.value)
            return {
                "action": "recall_user",
                "items": items,
                "count": len(items),
                "response": f"I currently remember {len(items)} facts and preferences about you."
            }

        # 4. What do you know about this project
        if "what do you know about this project" in text_lower or "what do you remember about this project" in text_lower:
            target_proj = project_id or "current_project"
            items = self.what_saarthi_knows(user_id=user_id, project_id=target_proj)
            return {
                "action": "recall_project",
                "project_id": target_proj,
                "items": items,
                "count": len(items),
                "response": f"I have {len(items)} context items remembered for project '{target_proj}'."
            }

        # 5. Project Remember Command: 'Remember this project uses [X]'
        proj_match = re.search(r"(?i)^remember (?:that )?this project (?:uses|requires|is|has) (.*)", text)
        if proj_match:
            fact = proj_match.group(1).strip()
            target_proj = project_id or "default_project"
            mem = self.create_project_memory(
                project_id=target_proj,
                content=f"Project uses {fact}",
                user_id=user_id,
                importance=8,
                provenance=MemoryProvenance.USER_EXPLICIT
            )
            return {
                "action": "remember_project",
                "memory": mem.model_dump(),
                "response": f"Remembered for project '{target_proj}': Project uses {fact}."
            }

        # 6. Preference Remember Command: 'Remember that I prefer [X]'
        pref_match = re.search(r"(?i)^remember (?:that )?i prefer (.*)", text)
        if pref_match:
            pref = pref_match.group(1).strip()
            mem = self.create_preference(
                content=f"Prefers {pref}",
                user_id=user_id,
                importance=8,
                scope=MemoryScope.PROJECT if project_id else MemoryScope.GLOBAL_USER,
                project_id=project_id,
                provenance=MemoryProvenance.USER_EXPLICIT
            )
            return {
                "action": "remember_preference",
                "memory": mem.model_dump(),
                "response": f"Remembered preference: Prefers {pref}."
            }

        # 7. General Remember Command: 'Remember [X]'
        gen_match = re.search(r"(?i)^remember (?:that )?(.*)", text)
        if gen_match:
            fact = gen_match.group(1).strip()
            mem = self.create_fact(
                content=fact,
                source=MemoryProvenance.USER_EXPLICIT,
                importance=7,
                domain=domain,
                user_id=user_id,
                project_id=project_id,
                scope=MemoryScope.PROJECT if project_id else MemoryScope.GLOBAL_USER
            )
            return {
                "action": "remember_fact",
                "memory": mem.model_dump(),
                "response": f"Remembered: '{fact}'."
            }

        # 8. Memory Correction Command: 'The information you have about X is wrong'
        corr_match = re.search(r"(?i)the information you have about (.*?) is (?:wrong|incorrect)", text)
        if corr_match:
            subject = corr_match.group(1).strip()
            matches = self.store.list_memories(user_id=user_id, limit=50)
            target_mem = next((m for m in matches if subject.lower() in m.content.lower()), None)
            if target_mem:
                return {
                    "action": "identify_correction_target",
                    "target_memory_id": target_mem.id,
                    "target_content": target_mem.content,
                    "response": f"Found existing memory about '{subject}': '{target_mem.content}'. Please specify the replacement fact."
                }
            return {
                "action": "identify_correction_target",
                "target_memory_id": None,
                "response": f"No existing memory found concerning '{subject}'."
            }

        return None

    def explain_memory_provenance(self, memory_id: int) -> Optional[Dict[str, Any]]:
        m = self.store.get_memory(memory_id)
        if not m:
            return None
        return {
            "memory_id": m.id,
            "content": m.content,
            "source": m.provenance.value if hasattr(m.provenance, 'value') else str(m.provenance),
            "scope": m.scope.value if hasattr(m.scope, 'value') else str(m.scope),
            "confidence": m.confidence,
            "domain": m.domain,
            "explanation": f"Fact recorded via provenance '{m.provenance}' with scope '{m.scope}'."
        }

    def get_user_fact_summary(self, user_id: str = "default_local_user") -> List[Dict[str, Any]]:
        memories = self.list_all_memories(user_id=user_id)
        return [
            {
                "id": m["id"],
                "content": m["content"],
                "source": m.get("provenance") or m.get("source"),
                "domain": m.get("domain", "general")
            }
            for m in memories
        ]

    def reset_memory_store(self, user_id: str = "default_local_user") -> bool:
        self.store.clear_user_memories(user_id)
        return True


memory_manager = MemoryManager()

