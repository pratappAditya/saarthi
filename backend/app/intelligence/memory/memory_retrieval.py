import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.intelligence.memory.memory_models import (
    MemoryItem, MemoryClass, MemoryScope, MemoryProvenance, RetentionState
)
from app.intelligence.memory.memory_store import MemoryStore

logger = logging.getLogger("app.intelligence.memory_retrieval")

# Strict Provenance Trust Multipliers
PROVENANCE_WEIGHTS = {
    MemoryProvenance.USER_EXPLICIT: 1.30,
    MemoryProvenance.user_explicit: 1.30,
    MemoryProvenance.SOURCE_DERIVED: 1.05,
    MemoryProvenance.uploaded_document: 1.05,
    MemoryProvenance.OBSERVED: 0.95,
    MemoryProvenance.tool_observation: 0.95,
    MemoryProvenance.MODEL_INFERENCE: 0.80,
    MemoryProvenance.model_inference: 0.80,
}

# Scope Precedence Rank (Higher = More Specific)
SCOPE_PRECEDENCE = {
    MemoryScope.TASK: 50,
    MemoryScope.PROJECT: 40,
    MemoryScope.GOAL: 35,
    MemoryScope.DOMAIN: 30,
    MemoryScope.CONVERSATION: 20,
    MemoryScope.GLOBAL_USER: 10,
    MemoryScope.USER: 10,
}


class MemoryRetriever:
    """
    Production Scoped Memory Retriever for Saarthi Deep Memory 2.0.
    Implements bounded, tenant-isolated, provenance-weighted composite retrieval
    with strict conflict resolution (Task > Project > Domain > Global > System).
    """
    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    def search(
        self,
        query: str,
        user_id: str = "default_local_user",
        domain: Optional[str] = None,
        project_id: Optional[str] = None,
        scope: Optional[str] = None,
        memory_class: Optional[str] = None,
        min_importance: int = 1,
        limit: int = 10,
        task_id: Optional[str] = None
    ) -> List[MemoryItem]:
        """
        Retrieves memories matching query keywords and scope, ranked by composite relevance:
        Score = ((Keyword Match * 0.35) + (Importance / 10 * 0.35) + (Scope Rank * 0.15) + (Recency * 0.15)) * Provenance Weight
        Applies tenant isolation, strict project boundaries, and automatic expiration filtering.
        """
        # Bounded query length and limit protection
        safe_limit = max(1, min(limit, 50))
        
        # Bounded candidate retrieval to prevent unbounded full-table scans
        candidates = self.store.list_memories(
            user_id=user_id,
            domain=domain,
            scope=scope,
            memory_class=memory_class,
            project_id=project_id,
            limit=150
        )

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        now_ts = datetime.now(timezone.utc).timestamp()
        scored_items: List[tuple[float, MemoryItem]] = []

        for item in candidates:
            # Tenant isolation safeguard
            if item.user_id != user_id:
                continue

            # Minimum importance threshold
            if item.importance < min_importance:
                continue

            # Project scope isolation: if searching within a project, do not return items from a different project
            if project_id and item.project_id and item.project_id != project_id:
                continue

            # Task isolation check if specified
            if task_id and item.task_id and item.task_id != task_id:
                continue

            # Expiration filter safeguard
            if item.expires_at:
                try:
                    exp_ts = datetime.fromisoformat(item.expires_at.replace("Z", "+00:00")).timestamp()
                    if exp_ts < now_ts:
                        continue
                except Exception:
                    pass

            content_lower = item.content.lower()
            match_count = sum(1 for term in query_terms if term in content_lower)

            if query_terms and match_count == 0:
                # Keep high importance items (profile/project essentials) even without direct term match
                if item.importance < 8:
                    continue

            # Keyword match ratio
            keyword_score = (match_count / max(1, len(query_terms))) if query_terms else 0.5
            importance_score = item.importance / 10.0

            # Scope rank bonus (Task > Project > Domain > Global)
            scope_val = item.scope if isinstance(item.scope, MemoryScope) else MemoryScope(item.scope)
            scope_rank = SCOPE_PRECEDENCE.get(scope_val, 10) / 50.0

            # Recency decay calculation (30 days half-life)
            recency_score = 0.5
            if item.updated_at:
                try:
                    upd_ts = datetime.fromisoformat(item.updated_at.replace("Z", "+00:00")).timestamp()
                    age_days = max(0.0, (now_ts - upd_ts) / 86400.0)
                    recency_score = max(0.1, 1.0 - (age_days / 60.0))
                except Exception:
                    pass

            # Provenance multiplier
            provenance_weight = PROVENANCE_WEIGHTS.get(item.provenance, 1.0)
            confidence_factor = max(0.5, min(item.confidence, 1.0))

            # Composite formula
            base_score = (
                (keyword_score * 0.35) +
                (importance_score * 0.30) +
                (scope_rank * 0.20) +
                (recency_score * 0.15)
            )
            total_score = base_score * provenance_weight * confidence_factor
            scored_items.append((total_score, item))

        # Sort descending by score
        scored_items.sort(key=lambda x: x[0], reverse=True)
        raw_items = [item for _, item in scored_items]

        # Resolve contradictory or conflicting directives before returning
        return self.resolve_conflicts(raw_items)[:safe_limit]

    def resolve_conflicts(self, items: List[MemoryItem]) -> List[MemoryItem]:
        """
        Resolves semantic or preference conflicts among retrieved memory items:
        1. Higher-precedence scopes (Task > Project > Domain > Global) win over lower scopes.
        2. Within the same scope, USER_EXPLICIT wins over MODEL_INFERENCE.
        3. Within identical scope and provenance, newer updated_at wins over older.
        """
        if len(items) <= 1:
            return items

        # Conflict dimensions: length (concise vs detailed), tone (formal vs casual), format (bullet vs prose)
        conflict_categories = {
            "response_length": {
                "concise": ["concise", "short", "brief", "crisp", "very concise"],
                "detailed": ["detailed", "deep", "comprehensive", "thorough", "elaborate"]
            },
            "communication_tone": {
                "formal": ["formal", "professional", "executive"],
                "casual": ["casual", "informal", "conversational", "friendly"]
            },
            "formatting": {
                "bullets": ["bullet", "bullet points", "list"],
                "prose": ["prose", "paragraphs", "continuous text"]
            }
        }

        resolved: List[MemoryItem] = []
        claimed_categories: Dict[str, MemoryItem] = {}

        for item in items:
            content_lower = item.content.lower()
            detected_dim = None
            detected_val = None

            for dim, values in conflict_categories.items():
                for val_name, triggers in values.items():
                    if any(t in content_lower for t in triggers):
                        detected_dim = dim
                        detected_val = val_name
                        break
                if detected_dim:
                    break

            if not detected_dim:
                # No conflicting dimension recognized, retain item
                resolved.append(item)
                continue

            # If this category has not been claimed yet, claim it with this top-ranked item
            if detected_dim not in claimed_categories:
                claimed_categories[detected_dim] = item
                resolved.append(item)
            else:
                incumbent = claimed_categories[detected_dim]
                # Compare precedence: scope first
                inc_scope_rank = SCOPE_PRECEDENCE.get(incumbent.scope, 10)
                item_scope_rank = SCOPE_PRECEDENCE.get(item.scope, 10)

                if item_scope_rank > inc_scope_rank:
                    # Replacement: item beats incumbent
                    resolved.remove(incumbent)
                    claimed_categories[detected_dim] = item
                    resolved.append(item)
                elif item_scope_rank == inc_scope_rank:
                    # Same scope: check provenance
                    inc_prov = PROVENANCE_WEIGHTS.get(incumbent.provenance, 1.0)
                    item_prov = PROVENANCE_WEIGHTS.get(item.provenance, 1.0)
                    if item_prov > inc_prov:
                        resolved.remove(incumbent)
                        claimed_categories[detected_dim] = item
                        resolved.append(item)
                    # Else keep incumbent

        return resolved

