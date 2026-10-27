import hmac
import hashlib
import uuid
import json
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from app.db.connection import get_db_connection, with_db_retry
from app.db.auth import AuthRepository

SAARTHI_PLAN_PRICING = {
    "FREE": {"inr": 0, "usd": 0.00, "currency_inr": "INR", "currency_usd": "USD", "billing_type": "flat"},
    "STUDENT": {"inr": 99, "usd": 1.50, "currency_inr": "INR", "currency_usd": "USD", "billing_type": "flat"},
    "PERSONAL": {"inr": 399, "usd": 5.00, "currency_inr": "INR", "currency_usd": "USD", "billing_type": "flat"},
    "POWER": {"inr": 799, "usd": 10.00, "currency_inr": "INR", "currency_usd": "USD", "billing_type": "flat"},
    "TEAMS": {"inr": 699, "usd": 9.00, "currency_inr": "INR", "currency_usd": "USD", "billing_type": "per_user"},
    "ENTERPRISE": {"inr": 0, "usd": 0.00, "currency_inr": "INR", "currency_usd": "USD", "billing_type": "custom"}
}

def init_payment_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                plan_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'CREATED',
                payment_id TEXT,
                signature TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                provider TEXT NOT NULL,
                event_type TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
        """)
        conn.commit()

init_payment_tables()

class PaymentProvider(ABC):
    async def create_customer(self, name: str, email: str) -> str:
        return f"cust_{uuid.uuid4().hex[:8]}"

    async def create_subscription(self, customer_id: str, plan_id: str) -> Dict[str, Any]:
        return {"subscription_id": f"sub_{uuid.uuid4().hex[:8]}", "customer_id": customer_id, "plan_id": plan_id, "status": "active"}

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    @abstractmethod
    async def create_order(self, user_id: str, plan_name: str, currency: str = "INR") -> Dict[str, Any]:
        pass

    @abstractmethod
    async def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        pass

    @abstractmethod
    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        pass

class RazorpayPaymentProvider(PaymentProvider):
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "rzp_sandbox_key")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "rzp_sandbox_secret")

    async def create_customer(self, name: str, email: str) -> str:
        return f"cust_rzp_{uuid.uuid4().hex[:8]}"

    async def create_subscription(self, customer_id: str, plan_id: str) -> Dict[str, Any]:
        return {"subscription_id": f"sub_rzp_{uuid.uuid4().hex[:8]}", "customer_id": customer_id, "plan_id": plan_id, "status": "active"}

    async def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    async def create_order(self, user_id: str, plan_name: str, currency: str = "INR") -> Dict[str, Any]:
        plan_info = SAARTHI_PLAN_PRICING.get(plan_name.upper())
        if not plan_info:
            raise ValueError(f"Invalid plan name: {plan_name}")
            
        amount_paise = plan_info["inr"] * 100
        order_id = f"order_rzp_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO payment_orders (order_id, user_id, provider, plan_name, amount, currency, status, created_at, updated_at)
                VALUES (?, ?, 'RAZORPAY', ?, ?, 'INR', 'CREATED', ?, ?)
            """, (order_id, user_id, plan_name.upper(), amount_paise, now_str, now_str))
            conn.commit()

        return {
            "order_id": order_id,
            "amount": amount_paise,
            "currency": "INR",
            "key_id": self.key_id,
            "provider": "RAZORPAY",
            "status": "CREATED"
        }

    async def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        if not signature or not order_id or not payment_id:
            return False
        msg = f"{order_id}|{payment_id}"
        generated_sig = hmac.new(self.key_secret.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(generated_sig, signature)
        
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            order = cursor.execute("SELECT * FROM payment_orders WHERE order_id = ?", (order_id,)).fetchone()
            if order:
                status = "PAID" if is_valid else "FAILED"
                cursor.execute("""
                    UPDATE payment_orders SET payment_id = ?, signature = ?, status = ?, updated_at = ? WHERE order_id = ?
                """, (payment_id, signature, status, now_str, order_id))
                conn.commit()
                if is_valid:
                    AuthRepository.update_user_plan(order["user_id"], order["plan_name"])
        return is_valid

    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        if not signature or not payload:
            return {"status": "rejected", "verified": False, "event": None}
        expected_sig = hmac.new(self.key_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        verified = hmac.compare_digest(expected_sig, signature)
        try:
            data = json.loads(payload.decode('utf-8'))
        except Exception:
            data = {}
        event_id = data.get("event_id", f"evt_{uuid.uuid4().hex[:8]}")

        with get_db_connection() as conn:
            existing = conn.execute("SELECT id FROM webhook_events WHERE event_id = ?", (event_id,)).fetchone()
            if existing:
                return {"status": "duplicate", "processed": False, "event_id": event_id}
            
            conn.execute("INSERT INTO webhook_events (event_id, provider, event_type, processed_at) VALUES (?, 'RAZORPAY', ?, ?)",
                         (event_id, data.get("event", "payment.captured"), datetime.now(timezone.utc).isoformat()))
            conn.commit()

        return {"status": "processed", "verified": verified, "event": data.get("event")}

class StripePaymentProvider(PaymentProvider):
    def __init__(self, api_key: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.api_key = api_key or os.getenv("STRIPE_SECRET_KEY", "sk_test_sandbox")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_sandbox")

    async def create_order(self, user_id: str, plan_name: str, currency: str = "USD") -> Dict[str, Any]:
        plan_info = SAARTHI_PLAN_PRICING.get(plan_name.upper())
        if not plan_info:
            raise ValueError(f"Invalid plan name: {plan_name}")
            
        amount_cents = int(plan_info["usd"] * 100)
        order_id = f"order_stripe_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO payment_orders (order_id, user_id, provider, plan_name, amount, currency, status, created_at, updated_at)
                VALUES (?, ?, 'STRIPE', ?, ?, 'USD', 'CREATED', ?, ?)
            """, (order_id, user_id, plan_name.upper(), amount_cents, now_str, now_str))
            conn.commit()

        return {
            "order_id": order_id,
            "amount": amount_cents,
            "currency": "USD",
            "provider": "STRIPE",
            "client_secret": f"pi_{uuid.uuid4().hex[:16]}_secret",
            "status": "CREATED"
        }

    async def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        if not signature or not order_id or not payment_id:
            return False
        msg = f"{order_id}|{payment_id}"
        expected_sig = hmac.new(self.webhook_secret.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(expected_sig, signature)
        
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            order = cursor.execute("SELECT * FROM payment_orders WHERE order_id = ?", (order_id,)).fetchone()
            if order:
                status = "PAID" if is_valid else "FAILED"
                cursor.execute("""
                    UPDATE payment_orders SET payment_id = ?, signature = ?, status = ?, updated_at = ? WHERE order_id = ?
                """, (payment_id, signature, status, now_str, order_id))
                conn.commit()
                if is_valid:
                    AuthRepository.update_user_plan(order["user_id"], order["plan_name"])
        return is_valid

    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        if not signature or not payload:
            return {"status": "rejected", "verified": False, "event": None}
        try:
            data = json.loads(payload.decode('utf-8'))
        except Exception:
            data = {}
        event_id = data.get("event_id", data.get("id", f"evt_{uuid.uuid4().hex[:8]}"))

        with get_db_connection() as conn:
            existing = conn.execute("SELECT id FROM webhook_events WHERE event_id = ?", (event_id,)).fetchone()
            if existing:
                return {"status": "duplicate", "processed": False, "event_id": event_id}
            
            conn.execute("INSERT INTO webhook_events (event_id, provider, event_type, processed_at) VALUES (?, 'STRIPE', ?, ?)",
                         (event_id, data.get("type", "payment_intent.succeeded"), datetime.now(timezone.utc).isoformat()))
            conn.commit()

        expected_sig = hmac.new(self.webhook_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
        is_verified = hmac.compare_digest(expected_sig, signature)
        return {"status": "processed", "verified": is_verified, "event": data.get("type", "payment_intent.succeeded")}

class MockPaymentProvider(PaymentProvider):
    def __init__(self):
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.subscriptions: Dict[str, Dict[str, Any]] = {}

    def _check_production(self):
        is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")
        if is_prod:
            raise RuntimeError("MockPaymentProvider is strictly disabled in production/staging environments.")

    async def create_customer(self, name: str, email: str) -> str:
        self._check_production()
        customer_id = f"cust_mock_{uuid.uuid4().hex[:8]}"
        self.customers[customer_id] = {"customer_id": customer_id, "name": name, "email": email}
        return customer_id

    async def create_subscription(self, customer_id: str, plan_id: str) -> Dict[str, Any]:
        self._check_production()
        if customer_id not in self.customers:
            raise ValueError(f"Customer not found: {customer_id}")
        sub_id = f"sub_mock_{uuid.uuid4().hex[:8]}"
        sub_data = {"subscription_id": sub_id, "customer_id": customer_id, "plan_id": plan_id, "status": "active"}
        self.subscriptions[sub_id] = sub_data
        return sub_data

    async def cancel_subscription(self, subscription_id: str) -> bool:
        self._check_production()
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]["status"] = "canceled"
            return True
        return False

    async def create_order(self, user_id: str, plan_name: str, currency: str = "INR") -> Dict[str, Any]:
        self._check_production()
        return {"order_id": f"order_mock_{uuid.uuid4().hex[:8]}", "amount": 0, "currency": currency, "status": "CREATED"}

    async def verify_payment(self, order_id: str, payment_id: str, signature: str) -> bool:
        self._check_production()
        return bool(signature) and signature.startswith("mock_verified_")

    async def process_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        self._check_production()
        is_verified = bool(signature) and signature.startswith("mock_webhook_verified_")
        return {"event_type": "invoice.paid", "verified": is_verified}

class PaymentProviderFactory:
    @staticmethod
    def get_provider(provider_type: str = "razorpay") -> PaymentProvider:
        p_type = provider_type.lower()
        if p_type == "stripe":
            return StripePaymentProvider()
        elif p_type == "mock":
            return MockPaymentProvider()
        return RazorpayPaymentProvider()
