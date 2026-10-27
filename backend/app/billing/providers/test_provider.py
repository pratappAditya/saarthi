"""
Test Payment Provider (Phase 10).
Mock provider for automated integration testing and local offline execution.
"""

import os
import secrets
from typing import Dict, Any, Optional
from app.billing.provider_interface import PaymentProvider, WebhookVerifier


class TestPaymentProvider(PaymentProvider, WebhookVerifier):
    def __init__(self):
        self._orders: Dict[str, Dict[str, Any]] = {}

    @property
    def provider_id(self) -> str:
        return "TEST_PROVIDER"

    @property
    def is_live_mode(self) -> bool:
        return False

    async def create_order(
        self,
        user_id: str,
        plan_id: str,
        amount_paise: int,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        order_id = f"order_test_{secrets.token_hex(8)}"
        order_data = {
            "provider": self.provider_id,
            "order_id": order_id,
            "user_id": user_id,
            "plan_id": plan_id,
            "amount": amount_paise,
            "currency": currency,
            "status": "created",
            "metadata": metadata or {}
        }
        self._orders[order_id] = order_data
        return order_data

    def verify_payment_sync(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")
        if is_prod:
            return False
        return bool(signature) and (signature.startswith("test_sig_") or signature in ("valid_sig", "valid_test_sig"))

    async def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        return self.verify_payment_sync(order_id, payment_id, signature)

    async def refund_payment(
        self,
        payment_id: str,
        amount_paise: int,
        reason: str
    ) -> Dict[str, Any]:
        return {
            "refund_id": f"ref_test_{secrets.token_hex(6)}",
            "payment_id": payment_id,
            "amount": amount_paise,
            "status": "completed",
            "reason": reason
        }

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")
        if is_prod:
            return False
        return bool(signature) and (signature.startswith("test_webhook_") or signature == "valid_webhook_sig")

    def parse_event(self, payload: bytes) -> Dict[str, Any]:
        return {
            "event_id": f"evt_test_{secrets.token_hex(6)}",
            "event_type": "payment.captured",
            "payload": {}
        }


test_payment_provider = TestPaymentProvider()
