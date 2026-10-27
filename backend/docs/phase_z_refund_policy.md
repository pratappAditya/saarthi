# Phase Z 24-Hour Satisfaction Refund Policy Architecture

## Overview
Design specification for Saarthi's 24-hour satisfaction refund request system.
*Important Notice*: In accordance with Phase Z rules, this refund policy is a **DESIGN TARGET ONLY** and is **NOT active in production** during Phase Z.

---

## Technical Refund Policy Specification (Rule Z.6)

### 1. Eligibility Window
- **Eligibility**: Candidate requests a refund within **24 hours** of initial subscription purchase.
- **Scope**: Applies to first-time Student, Personal, and Power plan subscriptions.

### 2. Operational Workflow
1. **Request Submission**: Candidate submits refund request via `/api/billing/refund-request` or vendor portal.
2. **Provider Execution**: Razorpay / Stripe API triggers full refund to original payment source (UPI/Card).
3. **Entitlement Revocation**: License status transitions from `ACTIVE` to `REVOKED`. User entitlement falls back to `FREE` plan (`requires_watermark = True`).
4. **Anti-Abuse Controls**: System logs hardware fingerprint (`device_fingerprint`) and user ID to block repeated refund abuse across multiple accounts.

### 3. Separation of Concepts
- **Subscription Cancellation**: Stops future auto-renewals; user retains paid access until billing period end.
- **Refund Request**: Immediately cancels subscription, refunds funds, and revokes paid entitlement.
