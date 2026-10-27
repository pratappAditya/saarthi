# SAARTHI AI COMPANION — WINDOWS STORE COMMERCE ARCHITECTURE & DECISION RECORD
**Document Version:** 1.0.0  
**Publisher:** Trovane Technologies  
**Date:** October 2026  
**Status:** ARCHITECTURAL SPECIFICATION & DECISION RECORD (LIVE BILLING DISABLED)

---

## 1. Executive Summary

This document establishes the commercial billing architecture for **Saarthi AI Companion** on Windows Desktop and the Microsoft Store. It provides a formal comparison between:
1. **Option A: Microsoft Store Native Commerce (`Windows.Services.Store`)**
2. **Option B: External Commerce via Razorpay / Webhooks**

As mandated by product decisions, **live payment collection is strictly disabled** across all environments. Local desktop AI features remain fully functional without requiring a paid subscription.

---

## 2. Option Comparison Matrix

| Architectural Attribute | Option A: Microsoft Store Native Commerce (`Windows.Services.Store`) | Option B: External Commerce (Razorpay Test Mode / Direct) |
|---|---|---|
| **User Experience** | Seamless 1-click Windows native modal with Windows Hello / Microsoft Account. | In-app browser modal or web checkout redirect to Razorpay hosted checkout. |
| **Payment Methods** | Microsoft Account, Cards, PayPal, Carrier Billing, Regional Currencies (240+ markets). | UPI (India), NetBanking, RuPay, Visa, Mastercard, Wallets. |
| **Store Fee** | 12% on non-game desktop application subscriptions; 0% if using custom billing. | Standard payment gateway transaction fee (~2% for domestic cards/UPI). |
| **Backend Integration** | Microsoft Store Collections & Purchase REST APIs (B2B Server-to-Server). | Secure Order Creation, HMAC-SHA256 callback verification, Idempotent Webhooks. |
| **Licensing Source of Truth** | Windows Store License Manager + Saarthi Authoritative Entitlement Service. | Saarthi Authoritative Entitlement Service + PostgreSQL Billing DB. |
| **Cross-Platform Sync** | Requires bridging Microsoft Store ID with Saarthi Account via B2B Key. | Native: Unified across Windows Desktop, Web, and Admin Control Plane. |
| **Current Implementation Status** | Client WinRT API bridge specified; Partner Center Add-on IDs pending owner setup. | **Implemented & Sandbox Tested**: Provider-independent billing engine with Razorpay test mode. |

---

## 3. Detailed Architecture Specifications

### 3.1 Option A: Microsoft Store Commerce (`Windows.Services.Store`)

#### Client-Side Flow
1. Desktop shell acquires current `StoreContext`:
   ```csharp
   StoreContext storeContext = StoreContext.GetDefault();
   // Initialize with active window handle (IInitializeWithWindow)
   ```
2. App queries active subscriptions and product add-ons:
   ```csharp
   StoreAppLicense license = await storeContext.GetAppLicenseAsync();
   bool isProActive = license.AddOnLicenses.ContainsKey("saarthi_pro_monthly");
   ```
3. To trigger purchase:
   ```csharp
   StorePurchaseResult result = await storeContext.RequestPurchaseAsync("saarthi_pro_monthly");
   ```
4. Upon successful purchase, app obtains user purchase token (`CustomerCollectionsId`) and transmits it to Saarthi Backend for validation.

#### Server-Side Validation (Microsoft B2B Key Exchange)
1. Saarthi Backend requests Azure AD access token for `https://onstorepurchase.microsoft.com`.
2. Validates purchase with Microsoft Collections API:
   `POST https://purchase.mp.microsoft.com/v1.0/b2b/keys/renew`
3. Backend issues a cryptographically signed Entitlement JWT to the desktop client.

---

### 3.2 Option B: External Gateway (Razorpay Architecture)

#### Flow Diagram
```
[Desktop Client]                     [Saarthi Backend]                   [Razorpay Sandbox]
       |                                     |                                    |
       |--- 1. POST /api/payment/checkout -->|                                    |
       |    (plan_id, billing_cycle)         |--- 2. Create Order --------------->|
       |                                     |<-- 3. Return order_id -------------|
       |<-- 4. Return checkout parameters ---|                                    |
       |                                     |                                    |
       |--- 5. Collect Payment via Modal ---------------------------------------->|
       |<-- 6. Return payment_id, signature --------------------------------------|
       |                                     |                                    |
       |--- 7. POST /api/payment/verify ---->|                                    |
       |    (order_id, payment_id, sig)      |--- 8. Verify HMAC-SHA256 signature |
       |                                     |--- 9. Transition state: ACTIVE ----|
       |                                     |--- 10. Issue Entitlement JWT ----->|
       |<-- 11. Entitlement Granted ---------|                                    |
```

#### Security Invariants
1. **Fails-Closed on Live Keys:**
   ```python
   if raw_key.startswith("rzp_live_"):
       raise PermissionError("Live payment collection is disabled. Only test mode keys permitted.")
   ```
2. **Server-Side Price Authority:**
   Client never transmits the price amount. Plan prices (`plan_registry.py`) are strictly resolved on the server to prevent amount tampering.
3. **Cryptographic Signature Verification:**
   ```python
   expected = hmac.new(secret.encode(), f"{order_id}|{payment_id}".encode(), sha256).hexdigest()
   if not secrets.compare_digest(expected, signature):
       raise HTTPException(status_code=400, detail="Invalid payment signature")
   ```
4. **Authoritative Entitlements:**
   Desktop SQLite database flags are **never** trusted to grant paid capabilities. All gates require a valid, unexpired backend-signed entitlement token.

---

## 4. Architectural Recommendation

**Dual-Channel Hybrid Approach (Recommended):**
1. **Primary Store Listing:** Adopt **Option A (Microsoft Store Native Commerce)** for standard consumers acquiring Saarthi via the Microsoft Store. This minimizes checkout friction and avoids external payment skepticism.
2. **Enterprise & Academic Channels:** Retain **Option B (Direct Backend Commerce)** for team licensing, custom academic bundles, and institutional invoices.
3. **Current State:** Live transactions remain disabled. Test mode orders and webhook verification pass 100% of integration test suites (`test_phase10_billing.py`).

---

## 5. Owner Decision Checklist

Before activating commercial transactions:
- [ ] Choose primary commerce platform (Microsoft Store Native vs Razorpay vs Dual-Mode).
- [ ] Finalize pricing tiers in INR and USD (e.g., Free, Pro Monthly, Power Annual).
- [ ] If Option A: Register Add-on Product IDs in Microsoft Partner Center.
- [ ] If Option B: Complete Razorpay production merchant KYC and provide live webhook secrets via secure environment variables.
- [ ] Authorize live billing activation in writing.
