"""
Billing Service Wrapper (Phase 10).
Bridges legacy service calls to the canonical BillingEngine, PlanRegistry, and StateMachine.
Guarantees:
- Server-authoritative pricing (anti-price-tampering)
- Server-side cryptographic signature verification (removes arbitrary string bypasses)
- Plan versioning retention
- Server-side entitlement and quota synchronization
- Safe test-mode operation with hard-disabled live payments
"""

import json
import secrets
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import HTTPException

from app.db.connection import get_db_connection, with_db_retry
from app.billing.billing_engine import billing_engine
from app.billing.plan_registry import plan_registry
from app.billing.models import CancellationPolicy

PLAN_CATALOG = {
    "FREE": {"price_inr": 0, "price_usd": 0.00, "name": "Free Plan", "type": "INDIVIDUAL"},
    "STUDENT": {"price_inr": 99, "price_usd": 1.50, "name": "Student Plan", "type": "INDIVIDUAL"},
    "PERSONAL": {"price_inr": 399, "price_usd": 5.00, "name": "Personal Plan", "type": "INDIVIDUAL"},
    "POWER": {"price_inr": 799, "price_usd": 10.00, "name": "Power Plan", "type": "INDIVIDUAL"},
    "TEAMS": {"price_inr": 699, "price_usd": 9.00, "name": "Teams Plan", "type": "PER_USER"},
    "ENTERPRISE": {"price_inr": 0, "price_usd": 0.00, "name": "Enterprise Plan", "type": "CUSTOM"}
}


class BillingService:
    @classmethod
    def get_plan_catalog(cls) -> Dict[str, Any]:
        """Returns the canonical plan catalog from the PlanRegistry."""
        return plan_registry.get_catalog_dict()

    @classmethod
    @with_db_retry()
    def create_checkout_order(
        cls,
        user_id: str,
        plan_name: str,
        provider: str = "RAZORPAY",
        currency: str = "INR",
        seats: int = 1,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a checkout order validated against server-locked plan pricing."""
        return billing_engine.create_checkout_order(
            user_id=user_id,
            plan_id=plan_name,
            provider=provider,
            currency=currency,
            seats=seats,
            org_id=org_id
        )

    @classmethod
    @with_db_retry()
    def verify_payment_and_activate_subscription(
        cls,
        order_id: str,
        payment_id: str,
        signature: str,
        plan_name: Optional[str] = None,
        provider: str = "RAZORPAY"
    ) -> Dict[str, Any]:
        """
        Cryptographically verifies payment signature and activates subscription atomically.
        Fails if signature is invalid or forged.
        """
        return billing_engine.verify_payment_and_activate_subscription(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            plan_name=plan_name,
            provider=provider
        )

    @classmethod
    @with_db_retry()
    def process_webhook(
        cls,
        payload: bytes,
        signature: str,
        provider: str = "RAZORPAY"
    ) -> Dict[str, Any]:
        """Processes provider webhooks with cryptographic validation and deduplication."""
        return billing_engine.process_webhook(
            payload=payload,
            signature=signature,
            provider=provider
        )

    @classmethod
    @with_db_retry()
    def cancel_subscription(
        cls,
        subscription_id: str,
        user_id: str,
        policy: str = "immediate"
    ) -> Dict[str, Any]:
        """Cancels subscription and reverts user to FREE tier entitlements."""
        cancel_policy = CancellationPolicy.END_OF_PERIOD if policy == "end_of_period" else CancellationPolicy.IMMEDIATE
        return billing_engine.cancel_subscription(
            subscription_id=subscription_id,
            user_id=user_id,
            policy=cancel_policy
        )

    @classmethod
    @with_db_retry()
    def upgrade_or_downgrade(
        cls,
        subscription_id: str,
        user_id: str,
        new_plan_name: str,
        new_seats: int = 1
    ) -> Dict[str, Any]:
        """Upgrades or downgrades an active subscription and resyncs entitlements."""
        return billing_engine.upgrade_or_downgrade(
            subscription_id=subscription_id,
            user_id=user_id,
            new_plan_id=new_plan_name,
            new_seats=new_seats
        )

    @classmethod
    @with_db_retry()
    def process_refund(
        cls,
        payment_id: str,
        admin_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Processes a refund and transitions payment/subscription state."""
        return billing_engine.process_refund(
            payment_id=payment_id,
            actor_id=admin_id,
            reason=reason
        )

    @classmethod
    @with_db_retry()
    def get_user_invoices(cls, user_id: str) -> List[Dict[str, Any]]:
        """Returns all invoices associated with the user."""
        return billing_engine.get_user_invoices(user_id)

    @classmethod
    @with_db_retry()
    def get_user_subscriptions(cls, user_id: str) -> List[Dict[str, Any]]:
        """Returns all subscriptions associated with the user."""
        return billing_engine.get_user_subscriptions(user_id)
