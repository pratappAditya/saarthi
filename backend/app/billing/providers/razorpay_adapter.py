"""
Razorpay Adapter (Phase 10 - Billing & Monetization 2.0).
TEST MODE ONLY.
LIVE PAYMENT IS HARD-DISABLED.
Fails closed if any production/live key is detected.
"""

import os
import hmac
import hashlib
import json
import secrets
import logging
from typing import Dict, Any, Optional

from app.billing.provider_interface import PaymentProvider, WebhookVerifier

logger = logging.getLogger("app.billing.razorpay")


class RazorpayAdapter(PaymentProvider, WebhookVerifier):
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        # 1. LIVE PAYMENT SAFETY ENFORCEMENT
        # Live keys are strictly prohibited in Saarthi 2.0 Phase 10
        raw_key = key_id or os.getenv("RAZORPAY_KEY_ID") or os.getenv("RAZORPAY_TEST_KEY_ID") or "rzp_test_sandbox"
        raw_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET") or os.getenv("RAZORPAY_TEST_KEY_SECRET") or "rzp_test_secret"

        if raw_key.startswith("rzp_live_"):
            logger.critical("SECURITY INVARIANT VIOLATION: Razorpay Live Key detected! Live payments are disabled. Failing closed.")
            raise PermissionError("Live payment collection is disabled in Saarthi 2.0. Only test mode keys are permitted.")

        self._key_id = raw_key
        self._key_secret = raw_secret

    def configure_credentials(self, key_id: str, key_secret: str):
        """Allows updating test credentials. Hard-fails on production/live keys."""
        if key_id.startswith("rzp_live_"):
            logger.critical("SECURITY INVARIANT VIOLATION: Razorpay Live Key detected! Live payments are disabled. Failing closed.")
            raise PermissionError("Live payment collection is disabled in Saarthi 2.0. Only test mode keys are permitted.")
        self._key_id = key_id
        self._key_secret = key_secret

    def generate_test_webhook_signature(self, payload: bytes) -> str:
        """Helper for test suites to compute valid test webhook HMAC."""
        return hmac.new(self._key_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    @property
    def provider_id(self) -> str:
        return "RAZORPAY"

    @property
    def is_live_mode(self) -> bool:
        return False  # Strict guarantee: live payments remain disabled

    @property
    def key_id(self) -> str:
        return self._key_id

    async def create_order(
        self,
        user_id: str,
        plan_id: str,
        amount_paise: int,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Creates a mock/sandbox Razorpay order in test mode."""
        order_token = secrets.token_hex(10)
        order_id = f"order_rzp_test_{order_token}"

        return {
            "provider": self.provider_id,
            "order_id": order_id,
            "amount": amount_paise,
            "currency": currency,
            "key_id": self._key_id,
            "plan_id": plan_id,
            "status": "created",
            "test_mode": True
        }

    async def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        Cryptographic signature verification.
        Computes HMAC-SHA256 of 'order_id|payment_id' using key_secret.
        Allows explicit sandbox test signature tokens during automated test suite runs.
        """
        if not signature or not order_id or not payment_id:
            return False

        msg = f"{order_id}|{payment_id}".encode("utf-8")
        expected = hmac.new(self._key_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def verify_payment_sync(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """Synchronous cryptographic signature verification."""
        if not signature or not order_id or not payment_id:
            return False
        msg = f"{order_id}|{payment_id}".encode("utf-8")
        expected = hmac.new(self._key_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def refund_payment(
        self,
        payment_id: str,
        amount_paise: int,
        reason: str
    ) -> Dict[str, Any]:
        """Processes a sandbox refund in test mode."""
        refund_id = f"rfnd_rzp_test_{secrets.token_hex(8)}"
        return {
            "refund_id": refund_id,
            "payment_id": payment_id,
            "amount": amount_paise,
            "status": "processed",
            "reason": reason
        }

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Validates incoming Razorpay webhook signature."""
        if not signature or not payload:
            return False

        expected = hmac.new(self._key_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_event(self, payload: bytes) -> Dict[str, Any]:
        """Parses webhook JSON payload into normalized event dictionary."""
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception:
            data = {}

        return {
            "event_id": data.get("event_id") or data.get("id") or f"evt_rzp_{secrets.token_hex(8)}",
            "event_type": data.get("event") or "payment.captured",
            "payload": data
        }


razorpay_adapter = RazorpayAdapter()
