"""
Saarthi Billing & Monetization 2.0 (Phase 10).
Canonical Data Models, Enums, and State Definitions.
Provider-Independent Architecture.
"""

import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PlanId(str, Enum):
    FREE = "FREE"
    STUDENT = "STUDENT"
    PERSONAL = "PERSONAL"
    POWER = "POWER"
    TEAMS = "TEAMS"
    ENTERPRISE = "ENTERPRISE"


class SubscriptionStatus(str, Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    INCOMPLETE = "INCOMPLETE"
    PENDING = "PENDING"


class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    VOID = "VOID"
    OVERDUE = "OVERDUE"


class RefundStatus(str, Enum):
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BillingInterval(str, Enum):
    MONTH = "month"
    USER_MONTH = "user/month"
    CUSTOM = "custom"
    FOREVER = "forever"


class CancellationPolicy(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    END_OF_PERIOD = "END_OF_PERIOD"


class PlanDefinition(BaseModel):
    plan_id: PlanId
    name: str
    version: str = "v1.0"
    price_inr: int  # Rupee amount (integer)
    currency: str = "INR"
    billing_interval: BillingInterval
    description: str
    badge: str
    is_custom: bool = False
    seat_limit: Optional[int] = None
    effective_from: float = Field(default_factory=time.time)
    effective_until: Optional[float] = None
    limits: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)


class PlanVersionRecord(BaseModel):
    version_id: str
    plan_id: PlanId
    version: str
    price_inr: int
    currency: str = "INR"
    billing_interval: str
    capabilities_json: str
    limits_json: str
    effective_from: float
    effective_until: Optional[float] = None


class SubscriptionRecord(BaseModel):
    subscription_id: str
    user_id: str
    org_id: Optional[str] = None
    plan_id: PlanId
    plan_version: str = "v1.0"
    provider: str = "RAZORPAY"
    provider_sub_id: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    seat_count: int = 1
    price_per_unit_paise: int = 0
    total_amount_paise: int = 0
    currency: str = "INR"
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool = False
    canceled_at: Optional[str] = None
    ended_at: Optional[str] = None
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentRecord(BaseModel):
    payment_id: str
    order_id: str
    user_id: str
    org_id: Optional[str] = None
    subscription_id: Optional[str] = None
    plan_id: PlanId = PlanId.FREE
    provider: str = "RAZORPAY"
    provider_payment_id: Optional[str] = None
    amount_paise: int  # Amount in paise (1 INR = 100 paise)
    currency: str = "INR"
    status: PaymentStatus = PaymentStatus.CREATED
    signature: Optional[str] = None
    receipt_url: Optional[str] = None
    error_code: Optional[str] = None
    error_description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None


class InvoiceItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price_paise: int
    total_price_paise: int


class InvoiceRecord(BaseModel):
    invoice_id: str
    subscription_id: str
    user_id: str
    org_id: Optional[str] = None
    items: List[InvoiceItem] = Field(default_factory=list)
    subtotal_paise: int
    tax_paise: int = 0
    total_paise: int
    currency: str = "INR"
    status: InvoiceStatus = InvoiceStatus.PAID
    billing_reason: str = "SUBSCRIPTION_CYCLE"
    pdf_url: Optional[str] = None
    created_at: str
    paid_at: Optional[str] = None


class RefundRecord(BaseModel):
    refund_id: str
    payment_id: str
    user_id: str
    amount_paise: int
    currency: str = "INR"
    reason: str
    status: RefundStatus = RefundStatus.COMPLETED
    provider_refund_id: Optional[str] = None
    created_at: str


class WebhookEventRecord(BaseModel):
    event_id: str
    provider: str
    event_type: str
    payload_hash: str
    processed_at: str
    status: str = "PROCESSED"


class BillingAuditEvent(BaseModel):
    audit_id: str
    actor_id: str
    action: str
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: str

