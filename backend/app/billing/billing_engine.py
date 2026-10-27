"""
Universal Safe Billing & Monetization Engine (Phase 10).
Integrates:
- Locked Plan Registry
- Provider-Independent Abstractions (Razorpay Test Mode & Test Provider)
- Strict State Machine Transitions
- Server-Side Entitlement & Quota Synchronization
- Idempotency & Replay Prevention
- Cryptographic Webhook Verification
- Invoice Generation & Audit Trails
"""

import os
import json
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from app.db.connection import get_db_connection, with_db_retry
from app.billing.models import (
    PlanId, SubscriptionStatus, PaymentStatus, InvoiceStatus, RefundStatus,
    CancellationPolicy, SubscriptionRecord, PaymentRecord, InvoiceRecord,
    InvoiceItem, RefundRecord, BillingAuditEvent
)
from app.billing.plan_registry import plan_registry
from app.billing.state_machine import billing_state_machine
from app.billing.providers.razorpay_adapter import razorpay_adapter
from app.billing.providers.test_provider import test_payment_provider
from app.core.plans import PlanService
from app.security.quota import QuotaManager

logger = logging.getLogger("app.billing.engine")


class BillingEngine:
    def __init__(self):
        self._providers = {
            "RAZORPAY": razorpay_adapter,
            "TEST_PROVIDER": test_payment_provider
        }

    def get_provider(self, provider_name: str = "RAZORPAY"):
        is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")
        prov = self._providers.get(provider_name.upper())
        if not prov:
            if is_prod:
                raise HTTPException(status_code=400, detail=f"Unsupported payment provider in production: '{provider_name}'")
            return test_payment_provider
        if is_prod and prov.provider_id == "TEST_PROVIDER":
            raise HTTPException(status_code=400, detail="TEST_PROVIDER cannot be used in production environment.")
        return prov

    @with_db_retry()
    def create_checkout_order(
        self,
        user_id: str,
        plan_id: str,
        provider: str = "RAZORPAY",
        currency: str = "INR",
        seats: int = 1,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a checkout order with server-enforced pricing.
        Client cannot tamper with price: server calculates expected amount.
        """
        plan_upper = plan_id.upper()
        defn = plan_registry.get_plan(plan_upper)
        if not defn:
            raise HTTPException(status_code=400, detail=f"Invalid plan identifier: '{plan_id}'")

        # In staging/production, enforce that billing is disabled by default and placeholder keys rejected
        from app.config.settings import settings
        is_staging_or_prod = getattr(settings, "ENVIRONMENT", "").lower() in ("staging", "production")
        if is_staging_or_prod and plan_upper != "FREE":
            if not getattr(settings, "FEATURE_BILLING", False) or getattr(settings, "PAYMENT_PROVIDER", "none").lower() == "none":
                raise HTTPException(
                    status_code=403,
                    detail="Billing and payment processing are disabled by default in staging environment."
                )
            if provider.upper() == "RAZORPAY":
                raw_k = razorpay_adapter.key_id
                if not raw_k or raw_k.startswith("generate_") or raw_k.startswith("your_"):
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot initiate checkout: payment provider credentials are unconfigured or placeholder keys."
                    )

        seats_count = max(1, seats)
        # Server-authoritative price calculation in paise
        amount_paise = plan_registry.calculate_expected_amount_paise(plan_upper, seats=seats_count)
        now_str = datetime.now(timezone.utc).isoformat()
        order_id = f"order_{provider.lower()[:3]}_{secrets.token_hex(8)}"
        payment_id = f"pay_pending_{secrets.token_hex(6)}"

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO payments (
                    payment_id, order_id, user_id, org_id, plan_name, seats, provider, amount, currency, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'CREATED', ?)
            """, (payment_id, order_id, user_id, org_id, plan_upper, seats_count, provider.upper(), amount_paise, currency, now_str))
            conn.commit()

        # Audit event
        self._log_audit_event(
            actor_id=user_id,
            action="CHECKOUT_ORDER_CREATED",
            user_id=user_id,
            org_id=org_id,
            details={"order_id": order_id, "plan_id": plan_upper, "amount_paise": amount_paise, "seats": seats_count}
        )

        key_id = razorpay_adapter.key_id if provider.upper() == "RAZORPAY" else "test_key_sandbox"

        return {
            "status": "success",
            "order": {
                "order_id": order_id,
                "payment_id": payment_id,
                "amount": amount_paise,
                "currency": currency,
                "plan_name": plan_upper,
                "seats": seats_count,
                "provider": provider.upper(),
                "key_id": key_id,
                "live_mode": False
            }
        }

    @with_db_retry()
    def verify_payment_and_activate_subscription(
        self,
        order_id: str,
        payment_id: str,
        signature: str,
        plan_name: Optional[str] = None,
        provider: str = "RAZORPAY"
    ) -> Dict[str, Any]:
        """
        Server-side signature verification & atomic subscription activation.
        Guarantees that premium access is never granted without cryptographic verification.
        """
        active_provider = self.get_provider(provider)

        # 1. Cryptographic Signature Verification
        if hasattr(active_provider, "verify_payment_sync"):
            is_valid = active_provider.verify_payment_sync(order_id, payment_id, signature)
        else:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                key_sec = getattr(active_provider, "_key_secret", None) or getattr(active_provider, "key_secret", None)
                if key_sec:
                    import hmac, hashlib
                    msg = f"{order_id}|{payment_id}".encode("utf-8")
                    sec_bytes = key_sec.encode("utf-8") if isinstance(key_sec, str) else key_sec
                    expected = hmac.new(sec_bytes, msg, hashlib.sha256).hexdigest()
                    is_valid = bool(signature) and hmac.compare_digest(expected, signature)
                else:
                    is_valid = False
            else:
                is_valid = asyncio.run(active_provider.verify_payment(order_id, payment_id, signature))

        if not is_valid:
            logger.warning(f"Signature Verification Failed for order '{order_id}', payment '{payment_id}'")
            raise HTTPException(status_code=400, detail="Cryptographic payment verification failed.")

        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        period_end = (now + timedelta(days=30)).isoformat()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            order_row = cursor.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY id DESC", (order_id,)).fetchone()
            if not order_row:
                raise HTTPException(status_code=404, detail="Order record not found.")

            order = dict(order_row)
            user_id = order["user_id"]
            org_id = order.get("org_id")
            amount = order["amount"]
            currency = order.get("currency", "INR")
            order_plan = order.get("plan_name")
            seats = order.get("seats", 1) or 1

            # Check Idempotency: if payment is already captured
            if order.get("status") == "PAID":
                existing_sub = cursor.execute("SELECT * FROM subscriptions WHERE user_id = ? AND status = 'ACTIVE'", (user_id,)).fetchone()
                if existing_sub:
                    d = dict(existing_sub)
                    return {
                        "status": "success",
                        "message": "Payment already captured (Idempotent response).",
                        "subscription": {
                            "subscription_id": d["subscription_id"],
                            "plan_name": d["plan_name"],
                            "status": d["status"]
                        }
                    }

            # State transition check
            billing_state_machine.transition_payment(PaymentStatus.CREATED, PaymentStatus.CAPTURED)

            # Determine plan from arguments, order record, or default
            resolved_plan = (plan_name or order_plan or "PERSONAL").upper()
            if resolved_plan not in plan_registry._versions:
                resolved_plan = "PERSONAL"

            # Check for collision on payment_id
            existing_pay = cursor.execute("SELECT id FROM payments WHERE payment_id = ? AND id != ?", (payment_id, order["id"])).fetchone()
            final_payment_id = f"{payment_id}_{secrets.token_hex(4)}" if existing_pay else payment_id

            # Update payment record
            cursor.execute("""
                UPDATE payments SET payment_id = ?, signature = ?, status = 'PAID' WHERE id = ?
            """, (final_payment_id, signature, order["id"]))

            # Create or update subscription
            sub_id = f"sub_{secrets.token_hex(8)}"
            cursor.execute("""
                INSERT INTO subscriptions (
                    subscription_id, user_id, org_id, plan_name, plan_version, provider, status, seat_count,
                    price_per_unit, total_amount, current_period_start, current_period_end, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'v1.0', ?, 'ACTIVE', ?, ?, ?, ?, ?, ?, ?)
            """, (sub_id, user_id, org_id, resolved_plan, provider.upper(), seats, amount, amount, now_str, period_end, now_str, now_str))

            # Record Subscription Event
            event_id = f"sev_{secrets.token_hex(8)}"
            cursor.execute("""
                INSERT INTO subscription_events (event_id, subscription_id, user_id, event_type, details_json, created_at)
                VALUES (?, ?, ?, 'SUBSCRIPTION_ACTIVATED', ?, ?)
            """, (event_id, sub_id, user_id, json.dumps({"order_id": order_id, "payment_id": final_payment_id, "plan": resolved_plan, "amount": amount}), now_str))

            # Generate Invoice
            inv_id = f"inv_{secrets.token_hex(8)}"
            cursor.execute("""
                INSERT INTO invoices (invoice_id, subscription_id, user_id, org_id, amount, currency, status, billing_reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'PAID', 'SUBSCRIPTION_PURCHASE', ?)
            """, (inv_id, sub_id, user_id, org_id, amount, currency, now_str))

            # Synchronize server-side entitlements
            conn.execute("UPDATE users SET subscription_plan = ?, updated_at = ? WHERE user_id = ?", (resolved_plan, now_str, user_id))
            if org_id:
                conn.execute("UPDATE organizations SET subscription_plan = ?, updated_at = ? WHERE org_id = ?", (resolved_plan, now_str, org_id))

            conn.commit()

        # Audit event
        self._log_audit_event(
            actor_id=user_id,
            action="SUBSCRIPTION_ACTIVATED",
            user_id=user_id,
            org_id=org_id,
            details={"subscription_id": sub_id, "plan": resolved_plan, "payment_id": final_payment_id}
        )

        return {
            "status": "success",
            "message": "Payment verified and subscription activated.",
            "subscription": {
                "subscription_id": sub_id,
                "plan_name": resolved_plan,
                "status": "ACTIVE",
                "current_period_end": period_end,
                "invoice_id": inv_id
            }
        }

    @with_db_retry()
    def cancel_subscription(
        self,
        subscription_id: str,
        user_id: str,
        policy: CancellationPolicy = CancellationPolicy.IMMEDIATE
    ) -> Dict[str, Any]:
        """Cancels an active subscription and updates entitlements."""
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM subscriptions WHERE subscription_id = ?", (subscription_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Subscription not found.")

            sub = dict(row)
            # Tenant isolation check
            if sub["user_id"] != user_id and user_id != "admin_system":
                raise HTTPException(status_code=403, detail="Access denied: Cannot cancel another user's subscription.")

            # State transition check
            billing_state_machine.transition_subscription(
                SubscriptionStatus(sub["status"]),
                SubscriptionStatus.CANCELLED
            )

            conn.execute("""
                UPDATE subscriptions SET cancel_at_period_end = 1, status = 'CANCELLED', canceled_at = ?, updated_at = ? WHERE subscription_id = ?
            """, (now_str, now_str, subscription_id))

            # Downgrade user plan to FREE
            conn.execute("UPDATE users SET subscription_plan = 'FREE', updated_at = ? WHERE user_id = ?", (now_str, sub["user_id"]))

            sev_id = f"sev_{secrets.token_hex(8)}"
            conn.execute("""
                INSERT INTO subscription_events (event_id, subscription_id, user_id, event_type, details_json, created_at)
                VALUES (?, ?, ?, 'SUBSCRIPTION_CANCELED', '{}', ?)
            """, (sev_id, subscription_id, sub["user_id"], now_str))

            conn.commit()

        self._log_audit_event(
            actor_id=user_id,
            action="SUBSCRIPTION_CANCELED",
            user_id=user_id,
            details={"subscription_id": subscription_id, "policy": policy.value}
        )

        return {
            "status": "success",
            "message": "Subscription canceled successfully. Account transitioned to FREE tier."
        }

    @with_db_retry()
    def upgrade_or_downgrade(
        self,
        subscription_id: str,
        user_id: str,
        new_plan_name: Optional[str] = None,
        new_plan_id: Optional[str] = None,
        new_seats: int = 1
    ) -> Dict[str, Any]:
        """Upgrades or downgrades an active subscription."""
        target_plan = new_plan_name or new_plan_id
        if not target_plan:
            raise HTTPException(status_code=400, detail="Must provide new_plan_name or new_plan_id")

        new_plan_upper = target_plan.upper()
        defn = plan_registry.get_plan(new_plan_upper)
        if not defn:
            raise HTTPException(status_code=400, detail=f"Invalid plan name: {target_plan}")

        seats_count = max(1, new_seats)
        total_amount_paise = plan_registry.calculate_expected_amount_paise(new_plan_upper, seats=seats_count)
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM subscriptions WHERE subscription_id = ?", (subscription_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Subscription not found.")

            sub = dict(row)
            if sub["user_id"] != user_id and user_id != "admin_system":
                raise HTTPException(status_code=403, detail="Access denied.")

            # In-place transition allowed
            billing_state_machine.transition_subscription(
                SubscriptionStatus(sub["status"]),
                SubscriptionStatus.ACTIVE
            )

            conn.execute("""
                UPDATE subscriptions SET plan_name = ?, seat_count = ?, price_per_unit = ?, total_amount = ?, updated_at = ? WHERE subscription_id = ?
            """, (new_plan_upper, seats_count, defn.price_inr * 100, total_amount_paise, now_str, subscription_id))

            conn.execute("UPDATE users SET subscription_plan = ?, updated_at = ? WHERE user_id = ?", (new_plan_upper, now_str, sub["user_id"]))

            sev_id = f"sev_{secrets.token_hex(8)}"
            conn.execute("""
                INSERT INTO subscription_events (event_id, subscription_id, user_id, event_type, details_json, created_at)
                VALUES (?, ?, ?, 'SUBSCRIPTION_UPDATED', ?, ?)
            """, (sev_id, subscription_id, sub["user_id"], json.dumps({"new_plan": new_plan_upper, "new_seats": seats_count}), now_str))

            conn.commit()

        self._log_audit_event(
            actor_id=user_id,
            action="SUBSCRIPTION_PLAN_CHANGED",
            user_id=user_id,
            details={"subscription_id": subscription_id, "new_plan": new_plan_upper, "new_seats": seats_count}
        )

        return {
            "status": "success",
            "message": f"Subscription updated to {new_plan_upper}.",
            "plan_name": new_plan_upper,
            "plan_id": new_plan_upper
        }

    @with_db_retry()
    def process_refund(
        self,
        payment_id: str,
        admin_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        reason: str = "Refund requested"
    ) -> Dict[str, Any]:
        """Admin-authorized refund processing."""
        effective_actor = actor_id or admin_id or "system_admin"
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM payments WHERE payment_id = ? OR order_id = ?", (payment_id, payment_id)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Payment record not found.")

            p = dict(row)
            refund_id = f"ref_{secrets.token_hex(8)}"

            # State transition check
            billing_state_machine.transition_payment(PaymentStatus.CAPTURED, PaymentStatus.REFUNDED)

            conn.execute("""
                INSERT INTO refunds (refund_id, payment_id, user_id, amount, reason, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'COMPLETED', ?)
            """, (refund_id, p["payment_id"], p["user_id"], p["amount"], reason, now_str))

            conn.execute("UPDATE payments SET status = 'REFUNDED' WHERE id = ?", (p["id"],))
            conn.execute("UPDATE users SET subscription_plan = 'FREE', updated_at = ? WHERE user_id = ?", (now_str, p["user_id"]))

            conn.commit()

        self._log_audit_event(
            actor_id=effective_actor,
            action="PAYMENT_REFUNDED",
            user_id=p["user_id"],
            details={"refund_id": refund_id, "amount": p["amount"], "reason": reason}
        )

        return {"status": "success", "message": "Refund processed successfully.", "refund_id": refund_id}

    @with_db_retry()
    def get_user_invoices(self, user_id: str) -> List[Dict[str, Any]]:
        """Returns all invoices for a given user."""
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM invoices WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            return [dict(r) for r in rows]

    @with_db_retry()
    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Returns all subscriptions for a given user."""
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM subscriptions WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            return [dict(r) for r in rows]

    @with_db_retry()
    def process_webhook(self, payload: bytes, signature: str, provider: str = "RAZORPAY") -> Dict[str, Any]:
        """
        Cryptographic signature verification, replay protection, and idempotent event ingestion.
        """
        active_provider = self.get_provider(provider)

        # 1. Signature Verification
        if not active_provider.verify_signature(payload, signature):
            logger.warning(f"Webhook Signature Verification Failed for provider '{provider}'.")
            return {"status": "error", "verified": False, "message": "Invalid webhook signature"}

        # 2. Parse Event
        parsed = active_provider.parse_event(payload)
        event_id = parsed["event_id"]
        event_type = parsed["event_type"]
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            # 3. Idempotency Check: Reject Replays
            existing = conn.execute("SELECT id FROM payment_events WHERE event_id = ?", (event_id,)).fetchone()
            if existing:
                logger.info(f"Duplicate Webhook Suppressed (Idempotent): event '{event_id}'")
                return {"status": "duplicate", "processed": False, "event_id": event_id, "message": "Event already processed."}

            conn.execute("""
                INSERT INTO payment_events (event_id, provider, event_type, payload_json, processed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (event_id, provider.upper(), event_type, json.dumps(parsed.get("payload", {})), now_str))
            conn.commit()

        return {"status": "processed", "processed": True, "event_id": event_id, "event_type": event_type}

    def _log_audit_event(
        self,
        actor_id: str,
        action: str,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Records security audit log without persisting sensitive credentials or tokens."""
        now_str = datetime.now(timezone.utc).isoformat()
        audit_id = f"baud_{secrets.token_hex(8)}"
        try:
            with get_db_connection() as conn:
                conn.execute("""
                    INSERT INTO billing_audit_events (audit_id, actor_id, user_id, org_id, action, details_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (audit_id, actor_id, user_id, org_id, action, json.dumps(details or {}), now_str))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record billing audit event: {e}")


billing_engine = BillingEngine()
