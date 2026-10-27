"""
Research Cache Subsystem (Phase 7).
Caches parsed source evaluations and synthesis results with TTL, content hashing,
and mandatory bypass for temporal queries targeting 'latest', 'current', or 'today'.
Supports deterministic programmatic invalidation.
"""

import hashlib
import time
from typing import Dict, Any, Optional
from app.intelligence.research.evidence_models import ResearchSynthesisResult

DEFAULT_TTL_SECONDS = 3600 * 6  # 6 hours default cache TTL


class ResearchCache:
    def __init__(self):
        # Key: query_hash -> Dict[str, Any]
        self._cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _compute_key(query: str, domain: str, output_mode: str) -> str:
        raw = f"{query.strip().lower()}|{domain.strip().lower()}|{output_mode.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def is_bypass_query(query: str) -> bool:
        """
        Queries explicitly requesting real-time or latest information bypass cache.
        """
        q_lower = query.lower()
        bypass_tokens = ["latest", "current", "today", "now", "recent", "realtime", "live"]
        return any(t in q_lower for t in bypass_tokens)

    def get(self, query: str, domain: str = "general", output_mode: Optional[str] = None) -> Optional[ResearchSynthesisResult]:
        if self.is_bypass_query(query):
            return None

        if output_mode:
            key = self._compute_key(query, domain, output_mode)
            entry = self._cache.get(key)
            if entry and time.time() <= entry["expires_at"]:
                return entry["result"]

        q_clean = query.strip().lower()
        d_clean = domain.strip().lower()
        for k, v in list(self._cache.items()):
            if v["query"].strip().lower() == q_clean and v["domain"].strip().lower() == d_clean:
                if time.time() <= v["expires_at"]:
                    return v["result"]
                else:
                    del self._cache[k]

        return None

    def set(
        self,
        query: str,
        domain: str,
        output_mode: str,
        result: ResearchSynthesisResult,
        ttl_seconds: int = DEFAULT_TTL_SECONDS
    ):
        key = self._compute_key(query, domain, output_mode)
        self._cache[key] = {
            "query": query,
            "domain": domain,
            "output_mode": output_mode,
            "result": result,
            "created_at": time.time(),
            "expires_at": time.time() + ttl_seconds
        }

    def invalidate(self, query: Optional[str] = None):
        """
        Invalidates a specific query or clears entire cache if query is None.
        """
        if query is None:
            self._cache.clear()
        else:
            q_clean = query.strip().lower()
            keys_to_del = [k for k, v in self._cache.items() if q_clean in v["query"].lower()]
            for k in keys_to_del:
                del self._cache[k]

    def size(self) -> int:
        return len(self._cache)


research_cache = ResearchCache()
