import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.personalization.personalization_store import personalization_store
from app.intelligence.personalization.personalization_engine import personalization_engine
from app.intelligence.personalization.personalization_model import (
    PreferenceSource,
    ExpertiseLevel,
    UserPersonalizationProfile
)
from app.core.plans import PlanService, PLAN_FREE, PLAN_PERSONAL, PLAN_POWER, PLAN_TEAMS

client = TestClient(app)

def test_personalization_store_persistence():
    """TEST 1: Verify profile creation, explicit preferences, and SQLite persistence."""
    uid = "test_pers_user_1"
    personalization_store.reset_all(uid)

    prof = personalization_store.get_profile(uid)
    assert prof.user_id == uid
    assert prof.communication_style == "direct"

    # Set explicit preference
    item = personalization_store.set_explicit_preference(uid, "communication_style", "executive", "communication")
    assert item.source == PreferenceSource.USER_EXPLICIT
    assert item.confidence == 1.0

    fetched = personalization_store.get_profile(uid)
    assert fetched.communication_style == "executive"
    assert fetched.explicit_preferences["communication_style"] == "executive"

def test_inferred_preference_lifecycle_confirm_reject_forget():
    """TEST 2: Inferred preference creation, evidence provenance, confirmation, rejection, and forgetting."""
    uid = "test_pers_user_2"
    personalization_store.reset_all(uid)

    inferred = personalization_store.record_inferred_preference(
        user_id=uid,
        key="frequent_tool_browser",
        category="work",
        value=True,
        confidence=0.82,
        evidence="Observed repeated web searches in research tasks."
    )
    assert inferred is not None
    assert inferred.source == PreferenceSource.MODEL_INFERRED
    assert inferred.confidence == 0.82
    assert inferred.confirmed is False

    # Confirm preference
    confirmed_ok = personalization_store.confirm_preference(uid, "frequent_tool_browser")
    assert confirmed_ok is True
    prof = personalization_store.get_profile(uid)
    assert prof.inferred_preferences["frequent_tool_browser"].source == PreferenceSource.USER_CONFIRMED
    assert prof.inferred_preferences["frequent_tool_browser"].confidence == 1.0

    # Test rejection
    personalization_store.record_inferred_preference(
        user_id=uid,
        key="reject_candidate",
        category="proactivity",
        value="high",
        confidence=0.70,
        evidence="Proactive prompt dismissal"
    )
    rejected_ok = personalization_store.reject_preference(uid, "reject_candidate")
    assert rejected_ok is True
    prof2 = personalization_store.get_profile(uid)
    assert "reject_candidate" not in prof2.inferred_preferences

    # Test forgetting
    forgot_ok = personalization_store.forget_preference(uid, "frequent_tool_browser")
    assert forgot_ok is True
    prof3 = personalization_store.get_profile(uid)
    assert "frequent_tool_browser" not in prof3.inferred_preferences

def test_domain_expertise_model_and_overrides():
    """TEST 3: Domain expertise estimation, confidence, and explicit overrides."""
    uid = "test_pers_user_3"
    personalization_store.reset_all(uid)

    # Inferred advanced expertise
    exp = personalization_store.set_domain_expertise(
        user_id=uid,
        domain="cybersecurity",
        level=ExpertiseLevel.ADVANCED,
        confidence=0.78,
        evidence="Analyzed complex pentesting logs",
        explicit_override=False
    )
    assert exp.level == ExpertiseLevel.ADVANCED
    assert exp.explicit_override is False

    # Override to expert explicitly
    exp_override = personalization_store.set_domain_expertise(
        user_id=uid,
        domain="cybersecurity",
        level=ExpertiseLevel.EXPERT,
        confidence=1.0,
        evidence="Explicit user override in Personalization Dashboard",
        explicit_override=True
    )
    assert exp_override.level == ExpertiseLevel.EXPERT
    assert exp_override.explicit_override is True

def test_precedence_order_hierarchy():
    """TEST 4: Resolve preferences via 'Task > Project > Domain > Global > System Defaults' precedence."""
    uid = "test_pers_user_4"
    personalization_store.reset_all(uid)

    # 1. Global: concise
    personalization_store.set_explicit_preference(uid, "preferred_response_length", "concise")
    ctx_global = personalization_engine.build_personalization_context(user_id=uid)
    assert ctx_global.effective_response_length == "concise"
    assert ctx_global.precedence_scope == "Global Profile"

    # 2. Project Override: detailed
    personalization_store.set_project_override(uid, "proj_alpha", "preferred_response_length", "detailed")
    ctx_proj = personalization_engine.build_personalization_context(user_id=uid, project_id="proj_alpha")
    assert ctx_proj.effective_response_length == "detailed"
    assert "proj_alpha" in ctx_proj.precedence_scope

    # 3. Task Prompt Override: concise
    ctx_task = personalization_engine.build_personalization_context(
        user_id=uid,
        project_id="proj_alpha",
        task_prompt="Provide a concise brief on cybersecurity vulnerabilities."
    )
    assert ctx_task.effective_response_length == "concise"
    assert ctx_task.precedence_scope == "Task Prompt Override"

def test_prompt_adaptation_and_explanations():
    """TEST 5: System prompt adaptation and human-readable explanations."""
    uid = "test_pers_user_5"
    personalization_store.reset_all(uid)
    personalization_store.set_explicit_preference(uid, "technical_depth", "expert")
    personalization_store.set_explicit_preference(uid, "preferred_formatting", "bullet_points")

    ctx = personalization_engine.build_personalization_context(user_id=uid, domain="software")
    base_prompt = "You are Saarthi AI Operating Companion."
    adapted = personalization_engine.adapt_response_prompt(base_prompt, ctx)

    assert "expert domain knowledge" in adapted.lower() or "expert" in adapted.lower()
    assert "bullet points" in adapted.lower()

    explanation = personalization_engine.explain_personalization(ctx)
    assert explanation["technical_depth"] == "expert"
    assert len(explanation["explanations"]) >= 1

def test_learning_disabled_behavior():
    """TEST 6: Verify learning toggles halt inference generation."""
    uid = "test_pers_user_6"
    personalization_store.reset_all(uid)
    prof = personalization_store.get_profile(uid)
    prof.learning_enabled = False
    personalization_store.save_profile(prof)

    signal_res = personalization_engine.learn_interaction_signal(
        user_id=uid,
        signal_type="tool_used",
        signal_data={"tool_id": "terminal.execute"}
    )
    assert signal_res is None

def test_personalization_rest_apis():
    """TEST 7: REST API endpoints for profile, learned preferences, confirmation, rejection, expertise, and settings."""
    uid = "test_rest_user"
    client.post("/api/personalization/reset", json={"user_id": uid})

    # 1. GET profile
    resp1 = client.get(f"/api/personalization/profile?user_id={uid}")
    assert resp1.status_code == 200
    assert resp1.json()["profile"]["user_id"] == uid

    # 2. PATCH profile
    resp2 = client.patch("/api/personalization/profile", json={"user_id": uid, "communication_style": "explanatory"})
    assert resp2.status_code == 200
    assert resp2.json()["profile"]["communication_style"] == "explanatory"

    # 3. Explicit preference
    resp3 = client.post("/api/personalization/preference/explicit", json={"user_id": uid, "key": "tone", "value": "calm", "category": "communication"})
    assert resp3.status_code == 200

    # 4. Domain Expertise
    resp4 = client.post("/api/personalization/expertise", json={"user_id": uid, "domain": "software", "level": "expert"})
    assert resp4.status_code == 200
    assert resp4.json()["expertise"]["level"] == "expert"

    # 5. Explain Personalization
    resp5 = client.get(f"/api/personalization/explain?user_id={uid}&domain=software")
    assert resp5.status_code == 200
    assert "explanation" in resp5.json()

    # 6. Settings
    resp6 = client.get(f"/api/personalization/settings?user_id={uid}")
    assert resp6.status_code == 200
    assert resp6.json()["personalization_enabled"] is True
