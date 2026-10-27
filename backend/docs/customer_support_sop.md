# SAARTHI — CUSTOMER SUPPORT & RECOVERY STANDARD OPERATING PROCEDURES (SOP)

**Date**: August 18, 2026  
**Audience**: Saarthi Customer Support Operators & Systems Administrator

---

## 1. Overview & General Policy

All customer support recovery operations must be performed using the **Vendor Control Center Operator Interface** or authorized Vendor Server REST APIs with valid `X-Vendor-Admin-Key` authentication. Support operators must **NEVER** edit customer SQLite database files manually.

---

## 2. Standard Recovery Procedures

### Incident 1: Payment Succeeded but Activation Failed
- **Symptom**: Customer completed Razorpay payment, but client application remains on `UNLICENSED` / `FREE` tier.
- **Operator Action**:
  1. Open Vendor Control Center UI (`/vendor/customers`).
  2. Search for customer by email address.
  3. Verify payment transaction ID in Razorpay dashboard.
  4. Issue a new Ed25519 license token under the customer's plan (`STUDENT`, `PERSONAL`, `POWER`).
  5. Provide the activation token to the customer via secure email.

### Incident 2: Device Replacement / Machine Transfer
- **Symptom**: Customer purchased a new laptop and gets `DEVICE_LIMIT_EXCEEDED` error.
- **Operator Action**:
  1. Locate customer license in Vendor Control Center.
  2. Perform "Device Reset" in license management panel to clear bound hardware fingerprints.
  3. Customer enters key on new machine; client binds new hardware fingerprint (`CPU+MAC+OS`).

### Incident 3: Accidental License Suspension
- **Symptom**: Customer license status shows `SUSPENDED`.
- **Operator Action**:
  1. Call `/api/vendor/licenses/{id}/restore` endpoint via Vendor Control Center UI.
  2. System restores license status to `ACTIVE` and logs audit entry.

### Incident 4: Database Corruption / Re-installation
- **Symptom**: Customer reinstalled OS or lost local database file.
- **Operator Action**:
  1. Customer installs fresh Saarthi binary.
  2. Customer enters existing activation key in Pricing / Activation modal.
  3. Vendor server validates token and re-binds client; local database is re-initialized safely.

### Incident 5: Refund Request
- **Symptom**: Customer requests refund within 7-day policy.
- **Operator Action**:
  1. Process refund in Razorpay gateway dashboard.
  2. Call `/api/vendor/licenses/{id}/revoke` endpoint to set license status to `REVOKED`.
  3. Client application updates CRL cache on next sync and fails closed.

### Incident 6: Renewal Failure
- **Symptom**: Monthly subscription renewal did not automatically extend license expiry.
- **Operator Action**:
  1. Call `/api/vendor/licenses/{id}/renew` with `extension_days=30` (or `365` for yearly).
  2. Customer receives updated Ed25519 token.
