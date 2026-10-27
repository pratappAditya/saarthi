"""
Billing State Machine & Transition Enforcer (Phase 10).
Guarantees mathematical correctness of all Subscription, Payment, and Invoice state changes.
Rejects impossible, out-of-order, or invalid transitions.
"""

import logging
from typing import Dict, Set
from app.billing.models import SubscriptionStatus, PaymentStatus, InvoiceStatus, RefundStatus

logger = logging.getLogger("app.billing.state_machine")


SUBSCRIPTION_TRANSITIONS: Dict[SubscriptionStatus, Set[SubscriptionStatus]] = {
    SubscriptionStatus.PENDING: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.INCOMPLETE
    },
    SubscriptionStatus.TRIAL: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.EXPIRED
    },
    SubscriptionStatus.ACTIVE: {
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.PAUSED,
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.EXPIRED,
        SubscriptionStatus.ACTIVE  # In-place renewal or plan upgrade/downgrade
    },
    SubscriptionStatus.PAST_DUE: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.EXPIRED
    },
    SubscriptionStatus.PAUSED: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED
    },
    SubscriptionStatus.CANCELLED: {
        SubscriptionStatus.ACTIVE,  # Reactivation
        SubscriptionStatus.EXPIRED
    },
    SubscriptionStatus.EXPIRED: {
        SubscriptionStatus.ACTIVE  # Resubscription
    },
    SubscriptionStatus.INCOMPLETE: {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.CANCELLED
    }
}


PAYMENT_TRANSITIONS: Dict[PaymentStatus, Set[PaymentStatus]] = {
    PaymentStatus.CREATED: {
        PaymentStatus.AUTHORIZED,
        PaymentStatus.CAPTURED,
        PaymentStatus.FAILED
    },
    PaymentStatus.AUTHORIZED: {
        PaymentStatus.CAPTURED,
        PaymentStatus.FAILED
    },
    PaymentStatus.CAPTURED: {
        PaymentStatus.REFUNDED,
        PaymentStatus.PARTIALLY_REFUNDED
    },
    PaymentStatus.FAILED: set(),  # Terminal state
    PaymentStatus.REFUNDED: set(),  # Terminal state
    PaymentStatus.PARTIALLY_REFUNDED: {
        PaymentStatus.REFUNDED
    }
}


INVOICE_TRANSITIONS: Dict[InvoiceStatus, Set[InvoiceStatus]] = {
    InvoiceStatus.DRAFT: {
        InvoiceStatus.ISSUED,
        InvoiceStatus.VOID
    },
    InvoiceStatus.ISSUED: {
        InvoiceStatus.PAID,
        InvoiceStatus.OVERDUE,
        InvoiceStatus.VOID
    },
    InvoiceStatus.OVERDUE: {
        InvoiceStatus.PAID,
        InvoiceStatus.VOID
    },
    InvoiceStatus.PAID: {
        InvoiceStatus.VOID  # In case of voided/refunded chargeback
    },
    InvoiceStatus.VOID: set()  # Terminal state
}


class BillingStateMachine:
    @staticmethod
    def can_transition_subscription(current: SubscriptionStatus, target: SubscriptionStatus) -> bool:
        if current == target:
            return True
        allowed = SUBSCRIPTION_TRANSITIONS.get(current, set())
        return target in allowed

    @staticmethod
    def transition_subscription(current: SubscriptionStatus, target: SubscriptionStatus) -> SubscriptionStatus:
        if not BillingStateMachine.can_transition_subscription(current, target):
            msg = f"Illegal Subscription State Transition: '{current.value}' -> '{target.value}' is not permitted."
            logger.error(msg)
            raise ValueError(msg)
        return target

    @staticmethod
    def can_transition_payment(current: PaymentStatus, target: PaymentStatus) -> bool:
        if current == target:
            return True
        allowed = PAYMENT_TRANSITIONS.get(current, set())
        return target in allowed

    @staticmethod
    def transition_payment(current: PaymentStatus, target: PaymentStatus) -> PaymentStatus:
        if not BillingStateMachine.can_transition_payment(current, target):
            msg = f"Illegal Payment State Transition: '{current.value}' -> '{target.value}' is not permitted."
            logger.error(msg)
            raise ValueError(msg)
        return target

    @staticmethod
    def can_transition_invoice(current: InvoiceStatus, target: InvoiceStatus) -> bool:
        if current == target:
            return True
        allowed = INVOICE_TRANSITIONS.get(current, set())
        return target in allowed

    @staticmethod
    def transition_invoice(current: InvoiceStatus, target: InvoiceStatus) -> InvoiceStatus:
        if not BillingStateMachine.can_transition_invoice(current, target):
            msg = f"Illegal Invoice State Transition: '{current.value}' -> '{target.value}' is not permitted."
            logger.error(msg)
            raise ValueError(msg)
        return target


billing_state_machine = BillingStateMachine()
