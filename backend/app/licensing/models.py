from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class LicenseStatus(str, Enum):
    UNLICENSED = "UNLICENSED"
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    GRACE_PERIOD = "GRACE_PERIOD"
    GRACE_EXPIRED = "GRACE_EXPIRED"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    CANCELLED = "CANCELLED"
    CLOCK_TAMPERED = "CLOCK_TAMPERED"

class LicensePlan(str, Enum):
    FREE = "FREE"
    STUDENT = "STUDENT"
    PERSONAL = "PERSONAL"
    POWER = "POWER"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"

class Entitlements(BaseModel):
    plan: LicensePlan
    can_use_core_chat: bool = True
    can_use_standard_tools: bool = True
    can_use_privileged_terminal: bool = True
    optimized_for_job_applications: bool = True
    optimized_for_email_drafting: bool = True
    optimized_for_calendar: bool = True
    max_job_applications_per_month: int = -1  # -1 means unlimited, 3 for FREE
    max_history_messages: int = 16
    priority_support: bool = False
    requires_watermark: bool = True
    price_inr_monthly: int = 0
    price_usd_monthly: float = 0.0

    @classmethod
    def from_plan(cls, plan: LicensePlan) -> "Entitlements":
        if plan == LicensePlan.FREE:
            return cls(
                plan=LicensePlan.FREE,
                can_use_core_chat=True,
                can_use_standard_tools=True,
                can_use_privileged_terminal=False,
                optimized_for_job_applications=True,
                optimized_for_email_drafting=True,
                optimized_for_calendar=True,
                max_job_applications_per_month=3,
                max_history_messages=6,
                priority_support=False,
                requires_watermark=True,
                price_inr_monthly=0,
                price_usd_monthly=0.0
            )
        elif plan == LicensePlan.STUDENT:
            return cls(
                plan=LicensePlan.STUDENT,
                can_use_core_chat=True,
                can_use_standard_tools=True,
                can_use_privileged_terminal=False,
                optimized_for_job_applications=True,
                optimized_for_email_drafting=True,
                optimized_for_calendar=True,
                max_job_applications_per_month=-1,
                max_history_messages=12,
                priority_support=False,
                requires_watermark=False,
                price_inr_monthly=99,
                price_usd_monthly=1.50
            )
        elif plan in (LicensePlan.PERSONAL, LicensePlan.MONTHLY):
            return cls(
                plan=plan,
                can_use_core_chat=True,
                can_use_standard_tools=True,
                can_use_privileged_terminal=True,
                optimized_for_job_applications=True,
                optimized_for_email_drafting=True,
                optimized_for_calendar=True,
                max_job_applications_per_month=-1,
                max_history_messages=16,
                priority_support=False,
                requires_watermark=False,
                price_inr_monthly=399,
                price_usd_monthly=5.00
            )
        else: # POWER, YEARLY, CUSTOM
            return cls(
                plan=plan,
                can_use_core_chat=True,
                can_use_standard_tools=True,
                can_use_privileged_terminal=True,
                optimized_for_job_applications=True,
                optimized_for_email_drafting=True,
                optimized_for_calendar=True,
                max_job_applications_per_month=-1,
                max_history_messages=32,
                priority_support=True,
                requires_watermark=False,
                price_inr_monthly=799,
                price_usd_monthly=10.00
            )

class LicensePayload(BaseModel):
    license_id: str
    customer_id: str
    plan: LicensePlan
    device_fingerprint: str
    issued_at: str
    expires_at: str
    grace_period_days: int = 7
    nonce: str

class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    created_at: str

class LicenseRecord(BaseModel):
    license_id: str
    license_key: str
    customer_id: str
    plan: LicensePlan
    status: LicenseStatus
    max_devices: int = 2
    issued_at: str
    expires_at: str
    created_at: str

class DeviceActivation(BaseModel):
    activation_id: str
    license_id: str
    device_fingerprint: str
    device_name: Optional[str] = None
    activated_at: str
    last_seen_at: str

class AuditLogEntry(BaseModel):
    log_id: Optional[int] = None
    action: str
    target_type: str
    target_id: str
    actor: str
    details: Optional[str] = None
    timestamp: str

class LicenseActivationRequest(BaseModel):
    license_key: str
    device_name: Optional[str] = "Desktop Workstation"
    hardware_info: Optional[Dict[str, Any]] = None

class LicenseSyncRequest(BaseModel):
    activation_token: str
    device_fingerprint: str
