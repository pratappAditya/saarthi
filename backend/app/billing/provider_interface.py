"""
Provider-Independent Billing Abstraction (Phase 10).
Abstract Base Classes for Payment Providers and Webhook Verifiers.
Decouples core business logic from specific gateway implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PaymentProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier (e.g., 'RAZORPAY', 'STRIPE', 'TEST_PROVIDER')."""
        pass

    @property
    @abstractmethod
    def is_live_mode(self) -> bool:
        """Must return False in Saarthi 2.0 to ensure live payments remain disabled."""
        pass

    @abstractmethod
    async def create_order(
        self,
        user_id: str,
        plan_id: str,
        amount_paise: int,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Creates a provider payment order/intent."""
        pass

    @abstractmethod
    async def verify_payment(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """Verifies cryptographic signature returned from provider on checkout completion."""
        pass

    @abstractmethod
    async def refund_payment(
        self,
        payment_id: str,
        amount_paise: int,
        reason: str
    ) -> Dict[str, Any]:
        """Issues a refund against a captured payment."""
        pass


class WebhookVerifier(ABC):
    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Validates provider HMAC or asymmetric signature on incoming webhook payloads."""
        pass

    @abstractmethod
    def parse_event(self, payload: bytes) -> Dict[str, Any]:
        """Normalizes provider-specific webhook payload into canonical event dictionary."""
        pass
