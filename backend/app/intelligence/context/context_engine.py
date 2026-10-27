import logging
from typing import Dict, Any, List, Optional
from app.intelligence.context.context_sources import (
    ContextBundle, UserContext, ConversationContext,
    MemoryContext, DomainContext
)
from app.intelligence.memory.memory_manager import memory_manager
from app.intelligence.domains.domain_router import domain_router
from app.intelligence.personalization.personalization_engine import personalization_engine
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.context_engine")

class ContextEngine:
    @staticmethod
    def build_context_bundle(
        user_message: str,
        session_id: str = "default_session",
        user_id: str = "default_local_user",
        project_id: Optional[str] = None,
        recent_history: Optional[List[Dict[str, Any]]] = None,
        attachment_id: Optional[str] = None
    ) -> ContextBundle:
        """
        Assembles intentional, structured ContextBundle incorporating UserContext,
        ConversationContext, MemoryContext, DomainContext, PersonalizationContext,
        and Multimodal Uploaded Evidence.
        """
        # 1. Domain Classification
        domain_info = domain_router.classify_domain(user_message)
        active_domain = domain_info["domain"]
        domain_pack_id = domain_info["domain_pack_id"]

        # 2. Plan Entitlement
        current_plan = get_current_plan(user_id)

        # 3. Retrieve Intentional Memories
        retrieved = memory_manager.search_memories(
            query=user_message,
            domain=active_domain,
            limit=5,
            user_id=user_id
        )
        mem_texts = [m["content"] for m in retrieved]

        # 4. Build Personalization Context with Precedence Hierarchy
        pers_ctx = personalization_engine.build_personalization_context(
            user_id=user_id,
            domain=active_domain,
            project_id=project_id,
            task_prompt=user_message
        )

        user_ctx = UserContext(user_id=user_id, plan_id=current_plan, preferred_domain=active_domain)
        conv_ctx = ConversationContext(session_id=session_id, recent_messages=recent_history or [])
        mem_ctx = MemoryContext(profile_facts=mem_texts, relevant_memories=mem_texts)
        
        # Multi-domain sequence detection
        seq = domain_router.detect_domain_sequence(user_message)
        subdomains = [item["domain"] for item in seq]
        dom_ctx = DomainContext(
            active_domain=active_domain,
            active_domain_pack=domain_pack_id,
            active_subdomains=subdomains
        )

        # 5. Ingest Multimodal Uploaded Evidence
        uploaded_evidence = []
        source_claims = []
        if attachment_id:
            from app.intelligence.multimodal.attachment_manager import attachment_manager
            att = attachment_manager.get_attachment(attachment_id, user_id=user_id)
            if att:
                evidence_entry = {
                    "attachment_id": att.id,
                    "filename": att.filename,
                    "mime_type": att.mime_type,
                    "evidence_class": "SOURCE-DERIVED",
                    "text_preview": (att.extracted_text or "")[:500],
                    "ocr_text": att.ocr_text or "",
                    "page_count": att.page_count or 1
                }
                uploaded_evidence.append(evidence_entry)
                source_claims.append({
                    "claim": f"Derived from uploaded document {att.filename}",
                    "source": att.filename,
                    "provenance": "SOURCE-DERIVED"
                })

        return ContextBundle(
            user_context=user_ctx,
            conversation_context=conv_ctx,
            memory_context=mem_ctx,
            domain_context=dom_ctx,
            personalization_context=pers_ctx,
            verified_facts=[{"fact": f"User prompt input: {user_message}", "provenance": "user_explicit_input"}],
            uploaded_evidence=uploaded_evidence,
            source_claims=source_claims,
            model_inferences=[]
        )

context_engine = ContextEngine()
