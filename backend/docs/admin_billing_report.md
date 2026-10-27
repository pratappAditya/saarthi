# Saarthi Admin Billing & Governance Report

## Executive Summary
The Admin Billing Control Plane (`AdminBillingService`, `/api/admin/billing/*`) provides real-time operational visibility into Saarthi's revenue metrics, active subscriptions, seat utilization, refund processing, and audit history.

---

## 1. Key Metrics & Analytics Capabilities

The Admin Billing Overview (`/api/admin/billing/overview`) computes business health metrics dynamically across all user accounts:

- **Monthly Recurring Revenue (MRR)**: Sum of all active monthly subscription prices.
- **Annual Recurring Revenue (ARR)**: `MRR * 12`.
- **Active Subscriptions**: Count of subscriptions in `ACTIVE` or `GRACE_PERIOD` status.
- **Churn Rate**: Percentage of canceled subscriptions over total historical subscriptions.
- **Seat Utilization**: Total allocated seats across `TEAMS` organizations vs. active team member accounts.

---

## 2. Operational Control Capabilities

- **Subscription Management**: Admin list and filter views for all user subscriptions, status overrides, and tier inspections (`/api/admin/billing/subscriptions`).
- **Payment & Invoice Logs**: Complete historical records of payment transactions, payment gateway references, and download links (`/api/admin/billing/payments`, `/api/admin/billing/invoices`).
- **Refund Execution**: `/api/admin/billing/refunds/process` allows authorized admins (`SUPER_ADMIN`, `ADMIN`) to process partial or full refunds, issuing audit logs and automatically revoking paid plan entitlements.
- **Audit Timeline**: `/api/admin/billing/audit` lists all billing operations with strict payload sanitization (masking secret keys, API signatures, and token hashes).
