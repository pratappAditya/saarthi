"""
Phase 10 — Billing + Monetization 2.0 Comprehensive Test Suite.
Validates:
1. Canonical Locked Plan Registry & Pricing (INR)
2. Plan Versioning & Enterprise Custom Architecture
3. Server-Authoritative Pricing (Anti-Price-Tampering)
4. Cryptographic Signature Verification & Forgery Rejection
5. Elimination of Length-Based Signature Bypass Loophole
6. Subscription Lifecycle (Create, Verify, Upgrade, Downgrade, Cancel)
7. State Machine Transitions & Rejection of Illegal Transitions
8. Webhook Signature Verification, Idempotency & Replay Prevention
9. Teams Per-Seat Pricing & Organization Scoping
10. Server-Side Entitlement & Quota Synchronization
11. Invoice Generation, Storage & Privacy Isolation
12. Refund Processing, Audit Events & Entitlement Revocation
13. Cross-Tenant and Cross-Organization Isolation
14. Hard-Disabled Live Payments (Safety Invariant: rzp_live_* rejection)
"""

import hmac
import hashlib
import json
import uuid
import secrets
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.db.connection import get_db_connection
from app.billing.plan_registry import plan_registry
from app.billing.models import (
    PlanId, SubscriptionStatus, PaymentStatus, InvoiceStatus, RefundStatus, CancellationPolicy
)
from app.billing.state_machine import billing_state_machine
from app.billing.billing_engine import billing_engine
from app.billing.providers.razorpay_adapter import razorpay_adapter
from app.billing.providers.test_provider import test_payment_provider
from app.services.billing_service import BillingService

client = TestClient(app)


def create_test_user(user_id: str, plan: str = "FREE") -> str:
    """Helper to populate valid user satisfying all DB foreign key & non-null constraints."""
    now_str = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users (
                user_id, email, password_hash, salt, full_name, is_verified, role, subscription_plan, created_at, updated_at
            ) VALUES (?, ?, 'hash', 'salt', 'Test User', 1, 'USER', ?, ?, ?)
        """, (user_id, f"{user_id}@saarthi.test", plan, now_str, now_str))
        conn.commit()
    return user_id


# ============================================================================
# 1. CANONICAL PLAN REGISTRY & LOCKED PRICING
# ============================================================================

def test_canonical_plans_and_locked_pricing():
    """Verify all 6 canonical plans are locked to exact specification."""
    plans = plan_registry.list_plans()
    plan_map = {p.plan_id: p for p in plans}

    assert PlanId.FREE in plan_map
    assert PlanId.STUDENT in plan_map
    assert PlanId.PERSONAL in plan_map
    assert PlanId.POWER in plan_map
    assert PlanId.TEAMS in plan_map
    assert PlanId.ENTERPRISE in plan_map

    # Locked Pricing Checks
    assert plan_map[PlanId.FREE].price_inr == 0
    assert plan_map[PlanId.STUDENT].price_inr == 99
    assert plan_map[PlanId.PERSONAL].price_inr == 399
    assert plan_map[PlanId.POWER].price_inr == 799
    assert plan_map[PlanId.TEAMS].price_inr == 699
    assert plan_map[PlanId.ENTERPRISE].is_custom is True

    # Check Paise conversion calculations
    assert plan_registry.calculate_expected_amount_paise(PlanId.FREE) == 0
    assert plan_registry.calculate_expected_amount_paise(PlanId.STUDENT) == 9900
    assert plan_registry.calculate_expected_amount_paise(PlanId.PERSONAL) == 39900
    assert plan_registry.calculate_expected_amount_paise(PlanId.POWER) == 79900
    assert plan_registry.calculate_expected_amount_paise(PlanId.TEAMS, seats=5) == 69900 * 5


# ============================================================================
# 2. PLAN VERSIONING
# ============================================================================

def test_plan_versioning_and_custom_enterprise():
    """Verify plan version retention and custom enterprise creation."""
    plan_v1 = plan_registry.get_plan(PlanId.PERSONAL)
    assert plan_v1.version == "v1.0"

    # Enterprise custom negotiated plan
    custom_ent = plan_registry.create_enterprise_custom_plan(
        client_name="GlobalCorp",
        negotiated_price_inr=150000,
        seat_limit=250,
        custom_capabilities={"dedicated_cluster": True, "custom_sla_hours": 1}
    )
    assert custom_ent.plan_id == PlanId.ENTERPRISE
    assert custom_ent.price_inr == 150000
    assert custom_ent.seat_limit == 250
    assert "dedicated_cluster" in custom_ent.capabilities
    assert custom_ent.version == "v1.0"


# ============================================================================
# 3. LIVE PAYMENT SAFETY CHECK (HARD-DISABLED)
# ============================================================================

def test_live_payments_strictly_disabled():
    """Ensure live payments cannot be instantiated or executed."""
    assert razorpay_adapter.is_live_mode is False
    assert test_payment_provider.is_live_mode is False

    # Attempting to configure live Razorpay keys MUST raise PermissionError
    with pytest.raises(PermissionError):
        razorpay_adapter.configure_credentials(key_id="rzp_live_secret123", key_secret="live_sec")

    # Re-verify that adapter remains in test mode
    assert razorpay_adapter.is_live_mode is False


# ============================================================================
# 4. PRICE TAMPERING PREVENTION (SERVER-AUTHORITATIVE)
# ============================================================================

def test_anti_price_tampering():
    """Verify client cannot tamper with price: server calculates expected amount."""
    user_id = f"user_tamper_{secrets.token_hex(4)}"
    create_test_user(user_id)

    # Client requests POWER plan (canonical: ₹799 = 79900 paise)
    res = billing_engine.create_checkout_order(
        user_id=user_id,
        plan_id="POWER",
        provider="TEST_PROVIDER",
        seats=1
    )
    assert res["status"] == "success"
    order = res["order"]
    assert order["amount"] == 79900
    assert order["plan_name"] == "POWER"

    # Verify order saved in database has exact canonical amount
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM payments WHERE order_id = ?", (order["order_id"],)).fetchone()
        assert row is not None
        assert row["amount"] == 79900
        assert row["plan_name"] == "POWER"


# ============================================================================
# 5. CRYPTOGRAPHIC SIGNATURE VERIFICATION & LOOPHOLE REMOVAL
# ============================================================================

def test_signature_verification_and_loophole_removal():
    """
    Ensure forged signatures fail, and the old legacy loophole
    (len(sig) > 10) is completely blocked.
    """
    user_id = f"user_crypto_{secrets.token_hex(4)}"
    create_test_user(user_id)

    order_res = billing_engine.create_checkout_order(
        user_id=user_id,
        plan_id="PERSONAL",
        provider="RAZORPAY"
    )
    order_id = order_res["order"]["order_id"]
    payment_id = f"pay_{secrets.token_hex(6)}"

    # 1. Arbitrary string longer than 10 characters MUST FAIL (legacy vulnerability eliminated)
    arbitrary_fake_sig = "this_is_a_very_long_forged_signature_string"
    with pytest.raises(HTTPException) as exc_info:
        billing_engine.verify_payment_and_activate_subscription(
            order_id=order_id,
            payment_id=payment_id,
            signature=arbitrary_fake_sig,
            provider="RAZORPAY"
        )
    assert exc_info.value.status_code == 400

    # 2. Correct HMAC-SHA256 signature MUST SUCCEED
    key_secret = b"rzp_test_secret"
    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(key_secret, msg, hashlib.sha256).hexdigest()

    act_res = billing_engine.verify_payment_and_activate_subscription(
        order_id=order_id,
        payment_id=payment_id,
        signature=valid_sig,
        provider="RAZORPAY"
    )
    assert act_res["status"] == "success"
    assert act_res["subscription"]["plan_name"] == "PERSONAL"
    assert act_res["subscription"]["status"] == "ACTIVE"


# ============================================================================
# 6. IDEMPOTENT PAYMENT CAPTURE
# ============================================================================

def test_idempotent_payment_capture():
    """Verify calling payment verification twice returns idempotent success without duplicate rows."""
    user_id = f"user_idem_{secrets.token_hex(4)}"
    create_test_user(user_id)

    order_res = billing_engine.create_checkout_order(
        user_id=user_id,
        plan_id="STUDENT",
        provider="RAZORPAY"
    )
    order_id = order_res["order"]["order_id"]
    payment_id = f"pay_{secrets.token_hex(6)}"

    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()

    # First attempt
    res1 = billing_engine.verify_payment_and_activate_subscription(
        order_id=order_id,
        payment_id=payment_id,
        signature=valid_sig
    )
    assert res1["status"] == "success"

    # Second attempt (same order_id and payment_id)
    res2 = billing_engine.verify_payment_and_activate_subscription(
        order_id=order_id,
        payment_id=payment_id,
        signature=valid_sig
    )
    assert res2["status"] == "success"
    assert "Idempotent" in res2["message"]

    # Verify no duplicate active subscriptions created
    with get_db_connection() as conn:
        subs = conn.execute("SELECT * FROM subscriptions WHERE user_id = ? AND status = 'ACTIVE'", (user_id,)).fetchall()
        assert len(subs) == 1


# ============================================================================
# 7. STATE MACHINE TRANSITIONS
# ============================================================================

def test_billing_state_machine():
    """Verify valid transitions succeed and illegal transitions are rejected."""
    # Valid Subscription transitions
    assert billing_state_machine.transition_subscription(SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE) == SubscriptionStatus.ACTIVE
    assert billing_state_machine.transition_subscription(SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELLED) == SubscriptionStatus.CANCELLED
    assert billing_state_machine.transition_subscription(SubscriptionStatus.CANCELLED, SubscriptionStatus.ACTIVE) == SubscriptionStatus.ACTIVE

    # Illegal Subscription transition: CANCELLED directly to PAST_DUE
    with pytest.raises(ValueError):
        billing_state_machine.transition_subscription(SubscriptionStatus.CANCELLED, SubscriptionStatus.PAST_DUE)

    # Valid Payment transitions
    assert billing_state_machine.transition_payment(PaymentStatus.CREATED, PaymentStatus.CAPTURED) == PaymentStatus.CAPTURED
    assert billing_state_machine.transition_payment(PaymentStatus.CAPTURED, PaymentStatus.REFUNDED) == PaymentStatus.REFUNDED

    # Illegal Payment transition: REFUNDED to CAPTURED
    with pytest.raises(ValueError):
        billing_state_machine.transition_payment(PaymentStatus.REFUNDED, PaymentStatus.CAPTURED)


# ============================================================================
# 8. SUBSCRIPTION LIFECYCLE (UPGRADE, DOWNGRADE, CANCEL)
# ============================================================================

def test_subscription_lifecycle_and_entitlement_sync():
    """
    Test full lifecycle:
    FREE -> Purchase STUDENT -> Upgrade to POWER -> Downgrade to PERSONAL -> Cancel (reverts to FREE)
    """
    user_id = f"user_life_{secrets.token_hex(4)}"
    create_test_user(user_id, plan="FREE")

    # Step 1: Initial Purchase (STUDENT)
    order_res = billing_engine.create_checkout_order(user_id=user_id, plan_id="STUDENT", provider="TEST_PROVIDER")
    order_id = order_res["order"]["order_id"]
    payment_id = f"pay_{secrets.token_hex(6)}"

    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()

    act_res = billing_engine.verify_payment_and_activate_subscription(order_id, payment_id, valid_sig)
    sub_id = act_res["subscription"]["subscription_id"]

    # Verify User table entitlement synchronized to STUDENT
    with get_db_connection() as conn:
        user = conn.execute("SELECT subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
        assert user["subscription_plan"] == "STUDENT"

    # Step 2: Upgrade to POWER
    up_res = billing_engine.upgrade_or_downgrade(subscription_id=sub_id, user_id=user_id, new_plan_id="POWER")
    assert up_res["status"] == "success"
    assert up_res["plan_id"] == "POWER"

    with get_db_connection() as conn:
        user = conn.execute("SELECT subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
        assert user["subscription_plan"] == "POWER"

    # Step 3: Downgrade to PERSONAL
    down_res = billing_engine.upgrade_or_downgrade(subscription_id=sub_id, user_id=user_id, new_plan_id="PERSONAL")
    assert down_res["status"] == "success"
    assert down_res["plan_id"] == "PERSONAL"

    with get_db_connection() as conn:
        user = conn.execute("SELECT subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
        assert user["subscription_plan"] == "PERSONAL"

    # Step 4: Cancellation
    cancel_res = billing_engine.cancel_subscription(subscription_id=sub_id, user_id=user_id, policy=CancellationPolicy.IMMEDIATE)
    assert cancel_res["status"] == "success"

    with get_db_connection() as conn:
        user = conn.execute("SELECT subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
        assert user["subscription_plan"] == "FREE"
        sub = conn.execute("SELECT status FROM subscriptions WHERE subscription_id = ?", (sub_id,)).fetchone()
        assert sub["status"] == "CANCELLED"


# ============================================================================
# 9. TEAMS BILLING & ORGANIZATION SCOPING
# ============================================================================

def test_teams_billing_and_seat_calculation():
    """Verify Teams per-user pricing (₹699/seat) and organization entitlement sync."""
    user_id = f"user_org_owner_{secrets.token_hex(4)}"
    org_id = f"org_{secrets.token_hex(4)}"
    create_test_user(user_id, plan="FREE")
    now_str = datetime.now(timezone.utc).isoformat()

    with get_db_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO organizations (org_id, name, owner_id, subscription_plan, seat_limit, created_at, updated_at) VALUES (?, 'Acme Corp', ?, 'FREE', 10, ?, ?)",
                     (org_id, user_id, now_str, now_str))
        conn.commit()

    # Checkout order for 10 seats of TEAMS
    order_res = billing_engine.create_checkout_order(
        user_id=user_id,
        plan_id="TEAMS",
        seats=10,
        org_id=org_id,
        provider="TEST_PROVIDER"
    )
    expected_amount = 69900 * 10  # ₹6,990 = 699,000 paise
    assert order_res["order"]["amount"] == expected_amount
    assert order_res["order"]["seats"] == 10

    order_id = order_res["order"]["order_id"]
    payment_id = f"pay_{secrets.token_hex(6)}"
    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()

    # Verify and activate
    billing_engine.verify_payment_and_activate_subscription(order_id, payment_id, valid_sig)

    # Verify Organization subscription_plan is synchronized to TEAMS
    with get_db_connection() as conn:
        org = conn.execute("SELECT subscription_plan FROM organizations WHERE org_id = ?", (org_id,)).fetchone()
        assert org["subscription_plan"] == "TEAMS"


# ============================================================================
# 10. WEBHOOK SECURITY, SIGNATURE & REPLAY PREVENTION
# ============================================================================

def test_webhook_security_and_deduplication():
    """Verify webhook cryptographic validation and duplicate event replay rejection."""
    event_id = f"evt_{secrets.token_hex(8)}"
    payload_dict = {
        "event_id": event_id,
        "event": "payment.captured",
        "entity": "payment",
        "amount": 39900
    }
    payload_bytes = json.dumps(payload_dict).encode("utf-8")

    # 1. Invalid signature rejection
    res_bad = billing_engine.process_webhook(
        payload=payload_bytes,
        signature="invalid_forged_webhook_signature",
        provider="RAZORPAY"
    )
    assert res_bad["status"] == "error"
    assert res_bad["verified"] is False

    # 2. Valid signature processing
    valid_sig = razorpay_adapter.generate_test_webhook_signature(payload_bytes)
    res_good = billing_engine.process_webhook(
        payload=payload_bytes,
        signature=valid_sig,
        provider="RAZORPAY"
    )
    assert res_good["status"] == "processed"
    assert res_good["processed"] is True

    # 3. Duplicate event replay rejection (Idempotency)
    res_duplicate = billing_engine.process_webhook(
        payload=payload_bytes,
        signature=valid_sig,
        provider="RAZORPAY"
    )
    assert res_duplicate["status"] == "duplicate"
    assert res_duplicate["processed"] is False


# ============================================================================
# 11. INVOICE SYSTEM & ISOLATION
# ============================================================================

def test_invoice_generation_and_tenant_isolation():
    """Verify invoice generation on subscription activation and strict user isolation."""
    user_a = f"user_inv_a_{secrets.token_hex(4)}"
    user_b = f"user_inv_b_{secrets.token_hex(4)}"
    create_test_user(user_a)
    create_test_user(user_b)

    # User A buys POWER plan
    order_a = billing_engine.create_checkout_order(user_id=user_a, plan_id="POWER", provider="TEST_PROVIDER")
    order_id = order_a["order"]["order_id"]
    pay_id = f"pay_{secrets.token_hex(6)}"
    msg = f"{order_id}|{pay_id}".encode("utf-8")
    sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()
    billing_engine.verify_payment_and_activate_subscription(order_id, pay_id, sig)

    # Invoices for User A
    invs_a = billing_engine.get_user_invoices(user_a)
    assert len(invs_a) >= 1
    assert invs_a[0]["amount"] == 79900
    assert invs_a[0]["status"] == "PAID"

    # User B should see 0 invoices (Tenant Isolation)
    invs_b = billing_engine.get_user_invoices(user_b)
    assert len(invs_b) == 0


# ============================================================================
# 12. REFUNDS & AUDIT TRAIL
# ============================================================================

def test_refund_processing_and_entitlement_revocation():
    """Verify refund transitions payment state, revokes paid plan, and logs audit record."""
    user_id = f"user_ref_{secrets.token_hex(4)}"
    admin_id = "admin_master_1"
    create_test_user(user_id)

    order = billing_engine.create_checkout_order(user_id=user_id, plan_id="PERSONAL", provider="TEST_PROVIDER")
    order_id = order["order"]["order_id"]
    pay_id = f"pay_{secrets.token_hex(6)}"
    msg = f"{order_id}|{pay_id}".encode("utf-8")
    sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()
    billing_engine.verify_payment_and_activate_subscription(order_id, pay_id, sig)

    # Verify user currently on PERSONAL
    with get_db_connection() as conn:
        u = conn.execute("SELECT subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
        assert u["subscription_plan"] == "PERSONAL"

    # Admin issues refund
    ref_res = billing_engine.process_refund(payment_id=pay_id, actor_id=admin_id, reason="Customer request satisfaction guarantee")
    assert ref_res["status"] == "success"
    assert "refund_id" in ref_res

    # Verify payment status is REFUNDED
    with get_db_connection() as conn:
        p = conn.execute("SELECT status FROM payments WHERE payment_id = ?", (pay_id,)).fetchone()
        assert p["status"] == "REFUNDED"
        # User reverted to FREE
        u = conn.execute("SELECT subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
        assert u["subscription_plan"] == "FREE"
        # Audit event recorded
        audit = conn.execute("SELECT * FROM billing_audit_events WHERE user_id = ? AND action = 'PAYMENT_REFUNDED'", (user_id,)).fetchone()
        assert audit is not None
        assert audit["actor_id"] == admin_id


# ============================================================================
# 13. CROSS-USER CANCELLATION ISOLATION (SECURITY)
# ============================================================================

def test_cross_user_cancellation_isolation():
    """Ensure User A cannot cancel User B's subscription."""
    user_victim = f"user_vic_{secrets.token_hex(4)}"
    user_attacker = f"user_att_{secrets.token_hex(4)}"
    create_test_user(user_victim)
    create_test_user(user_attacker)

    order = billing_engine.create_checkout_order(user_id=user_victim, plan_id="POWER", provider="TEST_PROVIDER")
    order_id = order["order"]["order_id"]
    pay_id = f"pay_{secrets.token_hex(6)}"
    msg = f"{order_id}|{pay_id}".encode("utf-8")
    sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()
    act = billing_engine.verify_payment_and_activate_subscription(order_id, pay_id, sig)
    sub_id = act["subscription"]["subscription_id"]

    # Attacker tries to cancel Victim's subscription
    with pytest.raises(HTTPException) as exc:
        billing_engine.cancel_subscription(subscription_id=sub_id, user_id=user_attacker)
    assert exc.value.status_code == 403


# ============================================================================
# 14. FRONTEND FAKE PAYMENT FORGERY BLOCK
# ============================================================================

def test_fake_payment_success_blocked():
    """Verify that claiming payment success without valid server cryptographic verification fails."""
    fake_order_id = "order_fake_999"
    fake_payment_id = "pay_fake_888"
    fake_sig = "fake_signature_client_attempt"

    with pytest.raises(HTTPException) as exc:
        billing_engine.verify_payment_and_activate_subscription(
            order_id=fake_order_id,
            payment_id=fake_payment_id,
            signature=fake_sig,
            provider="RAZORPAY"
        )
    assert exc.value.status_code in (400, 404)
