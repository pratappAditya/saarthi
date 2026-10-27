import pytest
import time
from datetime import datetime, timezone, timedelta
from app.intelligence.memory.memory_models import (
    MemoryClass, MemoryType, MemoryScope, MemoryProvenance, RetentionState, MemoryItem
)
from app.intelligence.memory.memory_store import MemoryStore
from app.intelligence.memory.memory_retrieval import MemoryRetriever
from app.intelligence.memory.memory_manager import MemoryManager
from app.intelligence.personalization.personalization_engine import PersonalizationEngine
from app.intelligence.personalization.personalization_store import PersonalizationStore
from app.intelligence.personalization.personalization_model import (
    UserPersonalizationProfile, ExpertiseLevel, DomainExpertise
)


@pytest.fixture
def temp_memory_store(tmp_path):
    db_file = str(tmp_path / "test_memory.db")
    store = MemoryStore(db_path=db_file)
    return store


@pytest.fixture
def memory_mgr(temp_memory_store):
    return MemoryManager(store=temp_memory_store)


@pytest.fixture
def temp_personalization_store(tmp_path):
    db_file = str(tmp_path / "test_personalization.db")
    return PersonalizationStore(db_path=db_file)


@pytest.fixture
def personalization_eng(temp_personalization_store):
    return PersonalizationEngine(store=temp_personalization_store)


# 1. CANONICAL MEMORY CLASSES TEST
def test_canonical_memory_classes():
    expected_classes = {
        "SHORT_TERM_CONTEXT",
        "CONVERSATION_MEMORY",
        "USER_MEMORY",
        "PROJECT_MEMORY",
        "GOAL_MEMORY",
        "DOMAIN_EXPERTISE",
        "WORKFLOW_MEMORY",
        "PREFERENCE_MEMORY",
        "VOICE_MEMORY"
    }
    actual_classes = {c.value for c in MemoryClass}
    assert expected_classes == actual_classes, f"Mismatch in canonical memory classes: {actual_classes ^ expected_classes}"
    # Backwards compatibility check
    assert MemoryType == MemoryClass


# 2. PROVENANCE CLASSES & INVARIANCE
def test_provenance_classes_and_invariance(memory_mgr):
    expected_provenances = {
        MemoryProvenance.USER_EXPLICIT,
        MemoryProvenance.SOURCE_DERIVED,
        MemoryProvenance.OBSERVED,
        MemoryProvenance.MODEL_INFERENCE
    }
    for prov in expected_provenances:
        assert prov in MemoryProvenance

    # Test multimodal intake preserves SOURCE_DERIVED unless explicitly confirmed
    unconfirmed = memory_mgr.create_multimodal_memory(
        content="Project deadline is October 10 from roadmap PDF",
        source_doc="roadmap_q4.pdf",
        user_id="user_alpha",
        project_id="proj_x",
        confirmed_by_user=False
    )
    assert unconfirmed.provenance == MemoryProvenance.SOURCE_DERIVED
    assert unconfirmed.metadata["user_confirmed"] is False

    # Confirm explicitly
    confirmed = memory_mgr.create_multimodal_memory(
        content="Project deadline is October 10 verified by user",
        source_doc="roadmap_q4.pdf",
        user_id="user_alpha",
        project_id="proj_x",
        confirmed_by_user=True
    )
    assert confirmed.provenance == MemoryProvenance.USER_EXPLICIT
    assert confirmed.confidence == 1.0


# 3. MEMORY SCOPES & PROJECT ISOLATION
def test_memory_scopes_and_isolation(memory_mgr):
    # Store project memory for Project A
    mem_a = memory_mgr.create_project_memory(
        project_id="proj_alpha",
        content="Project Alpha uses PostgreSQL and Redis",
        user_id="user_1"
    )
    # Store project memory for Project B
    mem_b = memory_mgr.create_project_memory(
        project_id="proj_beta",
        content="Project Beta uses MongoDB and Node.js",
        user_id="user_1"
    )
    # Store global user memory
    mem_global = memory_mgr.create_preference(
        content="Prefers dark theme syntax highlighting",
        user_id="user_1",
        scope=MemoryScope.GLOBAL_USER
    )

    # Retrieval for Project Alpha must NOT leak Project Beta
    retriever = memory_mgr.retriever
    results_alpha = retriever.search(query="database", user_id="user_1", project_id="proj_alpha")
    contents_alpha = [r.content for r in results_alpha]

    assert any("PostgreSQL" in c for c in contents_alpha)
    assert not any("MongoDB" in c for c in contents_alpha), "Project Beta memory leaked into Project Alpha retrieval!"


# 4. PREFERENCE PRECEDENCE: TASK > PROJECT > DOMAIN > GLOBAL > SYSTEM
def test_preference_precedence_hierarchy(personalization_eng, temp_personalization_store):
    user_id = "test_precedence_user"
    
    # 1. System Default is 'concise' (or default profile)
    # 2. Set Global Profile preference: 'detailed'
    profile = personalization_eng.get_profile(user_id)
    profile.preferred_response_length = "detailed"
    temp_personalization_store.save_profile(profile)

    ctx_global = personalization_eng.build_personalization_context(user_id=user_id)
    assert ctx_global.effective_response_length == "detailed"
    assert "Global Profile" in ctx_global.precedence_scope

    # 3. Add Domain Preference: 'balanced'
    temp_personalization_store.set_explicit_preference(
        user_id=user_id,
        key="engineering_response_depth",
        value="advanced",
        category="domain"
    )
    ctx_domain = personalization_eng.build_personalization_context(user_id=user_id, domain="engineering")
    assert ctx_domain.effective_technical_depth == "advanced"

    # 4. Add Project-Scoped Override: 'concise'
    temp_personalization_store.set_project_override(
        user_id=user_id,
        project_id="saarthi_project",
        key="preferred_response_length",
        value="concise"
    )
    ctx_proj = personalization_eng.build_personalization_context(
        user_id=user_id,
        domain="engineering",
        project_id="saarthi_project"
    )
    assert ctx_proj.effective_response_length == "concise"
    assert "Project Override" in ctx_proj.precedence_scope

    # 5. Task-Specific Override: 'very concise'
    # GLOBAL: detailed, PROJECT: concise, TASK: very concise -> Expected Task: very concise
    ctx_task = personalization_eng.build_personalization_context(
        user_id=user_id,
        domain="engineering",
        project_id="saarthi_project",
        task_prompt="Please generate the executive summary, make it very concise."
    )
    assert ctx_task.effective_response_length == "very concise", (
        f"Precedence failure: expected 'very concise', got '{ctx_task.effective_response_length}'"
    )
    assert ctx_task.precedence_scope == "Task Prompt Override"

    # Also test explicit task_overrides dictionary precedence
    ctx_task_direct = personalization_eng.build_personalization_context(
        user_id=user_id,
        domain="engineering",
        project_id="saarthi_project",
        task_overrides={"preferred_response_length": "very concise"}
    )
    assert ctx_task_direct.effective_response_length == "very concise"
    assert ctx_task_direct.precedence_scope == "Task Direct Override"


# 5. NATURAL LANGUAGE MEMORY DIRECTIVES
def test_natural_language_memory_directives(memory_mgr):
    user_id = "test_nl_user"
    proj_id = "proj_nlp"

    # 1. "Remember that I prefer concise reports."
    res1 = memory_mgr.process_memory_command(
        "Remember that I prefer concise reports.",
        user_id=user_id
    )
    assert res1 is not None
    assert res1["action"] == "remember_preference"
    assert "Prefers concise reports." in res1["response"]

    # 2. "Remember this project uses PostgreSQL."
    res2 = memory_mgr.process_memory_command(
        "Remember this project uses PostgreSQL.",
        user_id=user_id,
        project_id=proj_id
    )
    assert res2 is not None
    assert res2["action"] == "remember_project"
    assert "PostgreSQL" in res2["response"]

    # 3. "What do you remember about me?"
    res3 = memory_mgr.process_memory_command("What do you remember about me?", user_id=user_id)
    assert res3["action"] == "recall_user"
    assert res3["count"] >= 1

    # 4. "What do you know about this project?"
    res4 = memory_mgr.process_memory_command("What do you know about this project?", user_id=user_id, project_id=proj_id)
    assert res4["action"] == "recall_project"
    assert res4["count"] >= 1

    # 5. "The information you have about PostgreSQL is wrong."
    res5 = memory_mgr.process_memory_command("The information you have about PostgreSQL is wrong.", user_id=user_id)
    assert res5["action"] == "identify_correction_target"
    assert res5["target_memory_id"] is not None

    # 6. "Forget everything you know about this project."
    res6 = memory_mgr.process_memory_command(
        "Forget everything you know about this project.",
        user_id=user_id,
        project_id=proj_id
    )
    assert res6["action"] == "clear_project_memory"
    assert res6["deleted_count"] >= 1


# 6. MEMORY SAFETY & SECRET SCREENING
def test_memory_safety_secret_redaction(memory_mgr):
    dangerous_inputs = [
        "My OpenAI secret is sk-proj12345678901234567890abcdef",
        "The server password = SuperSecretP@ssword123!",
        "GitHub token is ghp_123456789012345678901234567890123456",
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...",
        "Use credit card 4111 2222 3333 4444 for billing"
    ]

    for secret in dangerous_inputs:
        with pytest.raises(ValueError, match="Security Policy Violation"):
            memory_mgr.create_fact(content=secret, user_id="user_sec")

        with pytest.raises(ValueError, match="Security Policy Violation"):
            memory_mgr.create_preference(content=secret, user_id="user_sec")


# 7. MEMORY RETRIEVAL COMPOSITE RANKING
def test_memory_retrieval_composite_ranking(memory_mgr):
    user_id = "user_composite"

    # User explicit fact
    item_explicit = memory_mgr.create_fact(
        content="User has 10 years experience in distributed systems architecture",
        source=MemoryProvenance.USER_EXPLICIT,
        importance=9,
        user_id=user_id
    )
    # Model inference
    item_inferred = memory_mgr.create_fact(
        content="May be interested in cloud systems architecture based on recent queries",
        source=MemoryProvenance.MODEL_INFERENCE,
        importance=4,
        user_id=user_id
    )

    results = memory_mgr.search_memories(
        query="architecture systems",
        user_id=user_id,
        limit=5
    )
    assert len(results) >= 2
    # USER_EXPLICIT with importance 9 should strictly rank before MODEL_INFERENCE
    assert results[0]["id"] == item_explicit.id
    assert results[0]["provenance"] == MemoryProvenance.USER_EXPLICIT.value


# 8. MEMORY CONFLICT RESOLUTION
def test_memory_conflict_resolution(memory_mgr):
    user_id = "user_conflict"

    # Global preference: detailed
    global_item = memory_mgr.create_preference(
        content="Prefers detailed comprehensive technical documentation",
        importance=7,
        user_id=user_id,
        scope=MemoryScope.GLOBAL_USER
    )
    # Project override: concise
    project_item = memory_mgr.create_preference(
        content="Prefers concise brief bullet reports for project alpha",
        importance=8,
        user_id=user_id,
        scope=MemoryScope.PROJECT,
        project_id="proj_alpha"
    )

    retriever = memory_mgr.retriever
    # Retrieval for project alpha should resolve conflicting length preference in favor of project scope
    resolved = retriever.search(
        query="prefers reports",
        user_id=user_id,
        project_id="proj_alpha",
        limit=5
    )
    resolved_contents = [r.content for r in resolved]
    assert any("concise" in c for c in resolved_contents)
    assert not any("detailed comprehensive" in c for c in resolved_contents)


# 9. MEMORY CORRECTION ELEVATES PROVENANCE
def test_memory_correction_elevates_provenance(memory_mgr):
    user_id = "user_corr"
    # Create an initial inferred fact
    orig = memory_mgr.create_fact(
        content="User primarily codes in Java",
        source=MemoryProvenance.MODEL_INFERENCE,
        user_id=user_id
    )
    assert orig.provenance == MemoryProvenance.MODEL_INFERENCE

    # User explicitly corrects it
    corrected = memory_mgr.correct_memory(
        memory_id=orig.id,
        new_content="User primarily codes in Rust and Python",
        user_id=user_id
    )
    assert corrected is not None
    assert corrected.content == "User primarily codes in Rust and Python"
    assert corrected.provenance == MemoryProvenance.USER_EXPLICIT
    assert corrected.confidence == 1.0


# 10. MEMORY DELETION & CACHE INVALIDATION
def test_memory_deletion_and_cache_invalidation(memory_mgr):
    user_id = "user_del"
    item = memory_mgr.create_fact(content="Temporary note to be forgotten", user_id=user_id)
    assert len(memory_mgr.list_all_memories(user_id=user_id)) == 1

    # Delete memory
    deleted = memory_mgr.forget(item.id, user_id=user_id)
    assert deleted is True

    # Ensure retrieval stops returning it immediately
    assert len(memory_mgr.list_all_memories(user_id=user_id)) == 0
    search_res = memory_mgr.search_memories(query="temporary note", user_id=user_id)
    assert len(search_res) == 0


# 11. EXPIRATION & AUTO-PRUNING
def test_memory_expiration_and_autopruning(memory_mgr):
    user_id = "user_exp"
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    future_iso = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    # Create expired item
    expired_item = memory_mgr.create_fact(
        content="Old temporary research session context",
        user_id=user_id,
        retention_state=RetentionState.EXPIRING,
        expires_at=past_iso
    )
    # Create active item
    active_item = memory_mgr.create_fact(
        content="Ongoing project milestone notes",
        user_id=user_id,
        retention_state=RetentionState.DURABLE,
        expires_at=future_iso
    )

    # Calling list_all_memories automatically triggers pruning
    active_items = memory_mgr.list_all_memories(user_id=user_id)
    ids = [m["id"] for m in active_items]

    assert expired_item.id not in ids, "Expired memory was not pruned!"
    assert active_item.id in ids


# 12. STRICT TENANT ISOLATION
def test_tenant_isolation(memory_mgr):
    user_a = "user_tenant_A"
    user_b = "user_tenant_B"

    item_a = memory_mgr.create_fact(content="Confidential proprietary info for User A", user_id=user_a)
    item_b = memory_mgr.create_fact(content="Confidential proprietary info for User B", user_id=user_b)

    # User A listing and searching
    list_a = memory_mgr.list_all_memories(user_id=user_a)
    search_a = memory_mgr.search_memories(query="Confidential", user_id=user_a)
    assert all(m["user_id"] == user_a for m in list_a)
    assert all(m["user_id"] == user_a for m in search_a)

    # User B listing and searching
    list_b = memory_mgr.list_all_memories(user_id=user_b)
    search_b = memory_mgr.search_memories(query="Confidential", user_id=user_b)
    assert all(m["user_id"] == user_b for m in list_b)
    assert all(m["user_id"] == user_b for m in search_b)

    # User B cannot delete User A's memory
    b_delete_a = memory_mgr.forget(item_a.id, user_id=user_b)
    assert b_delete_a is False
    # Memory for User A remains intact
    assert len(memory_mgr.list_all_memories(user_id=user_a)) == 1


# 13. VOICE MEMORY ISOLATION
def test_voice_memory_isolation(memory_mgr):
    user_id = "user_voice"
    v_mem = memory_mgr.create_voice_memory(
        content="Preferred Hindi-English mixed pronunciation for technical keywords",
        user_id=user_id,
        metadata={"speaking_rate": 1.1, "preferred_language": "hi-IN"}
    )
    assert v_mem.memory_class == MemoryClass.VOICE_MEMORY
    assert v_mem.metadata["speaking_rate"] == 1.1

    all_mems = memory_mgr.list_all_memories(user_id=user_id)
    assert len(all_mems) == 1
    assert all_mems[0]["memory_class"] == MemoryClass.VOICE_MEMORY.value


# 14. AGENT MEMORY AS CONTEXT NOT AUTHORIZATION
def test_agent_memory_as_context_not_authorization(memory_mgr):
    user_id = "user_agent_sec"
    # User memory indicates preference
    memory_mgr.create_preference(
        content="Automatically approve deployment scripts under 50 lines",
        user_id=user_id
    )
    # Verify that memory item exists as context
    mems = memory_mgr.search_memories(query="deployment scripts", user_id=user_id)
    assert len(mems) >= 1
    # Check that memory cannot bypass permission engine check
    from app.intelligence.permissions.permission_engine import permission_engine
    from app.intelligence.permissions.permission_models import PermissionStatus
    # Even if memory says 'automatically approve', permission engine requires explicit grant or confirmation
    req = permission_engine.request_permission(
        tool_id="system_exec",
        action_description="Deploy script",
        arguments={"command": "/deploy.sh"},
        user_id=user_id
    )
    assert req.status == PermissionStatus.PENDING, "Memory must never bypass system permission authorization!"
    assert req.status != PermissionStatus.APPROVED


# 15. "WHAT SAARTHI KNOWS" AUDIT INSPECTION
def test_what_saarthi_knows_inspection(memory_mgr):
    user_id = "user_audit"
    memory_mgr.create_fact(
        content="Speaks fluent Hindi and English",
        source=MemoryProvenance.USER_EXPLICIT,
        user_id=user_id
    )
    memory_mgr.create_project_memory(
        project_id="proj_saarthi",
        content="Saarthi project requires strict tenant isolation",
        user_id=user_id
    )

    audit_items = memory_mgr.what_saarthi_knows(user_id=user_id)
    assert len(audit_items) == 2
    for item in audit_items:
        assert "what" in item
        assert "why" in item
        assert "source" in item
        assert "scope" in item
        assert "confidence" in item
        assert "created_at" in item
        assert "updated_at" in item
        assert item["can_edit"] is True
        assert item["can_delete"] is True
