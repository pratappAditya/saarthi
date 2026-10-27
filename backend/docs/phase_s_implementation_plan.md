# Phase S Implementation Plan: Public Beta Growth, Free-Tier Watermark & Monetization Optimization

## Overview
Saarthi is now in **PUBLIC BETA OPEN** (v0.5.0-rc2 baseline).
The goal of Phase S is to optimize free-to-paid conversion, implement a subtle free-tier watermark on generated/exported documents, introduce a privacy-safe referral system, harden payment webhooks, instrument operational conversion metrics, and perform rigorous security and privacy regression testing.

---

## 1. Files to Modify

### Backend (`backend/app/`)
- `backend/app/licensing/models.py`:
  - Update `Entitlements` schema to add `requires_watermark: bool = True`.
  - Update `Entitlements.from_plan(plan)` factory to set `requires_watermark = True` for `FREE` and `False` for `STUDENT`, `PERSONAL`, `MONTHLY`, `POWER`, `YEARLY`, `CUSTOM`.
- `backend/app/licensing/client_manager.py`:
  - Pass `requires_watermark` entitlement in active and fallback license evaluations.
- `backend/app/api/career.py`:
  - Import watermark engine and telemetry logger.
  - Apply watermark on generated tailored resumes and cover letters when `requires_watermark` is `True`.
  - Add `/career/export-document` endpoint for clean document re-exporting.
- `backend/app/licensing/telemetry.py`:
  - Add conversion and monetization event tracking (`FREE_USER_ACTIVATED`, `DOCUMENT_GENERATED`, `WATERMARKED_EXPORT`, `PRICING_VIEWED`, `UPGRADE_PROMPT_SHOWN`, `CHECKOUT_STARTED`, `PAYMENT_SUCCESS`, etc.).
- `backend/app/api/routes.py`:
  - Add payment webhook verification routes for Razorpay/Stripe with signature validation and duplicate replay protection.
  - Add referral system routes (`GET /api/referrals`, `POST /api/referrals/redeem`).
  - Add monetization analytics endpoint (`GET /api/vendor/monetization-metrics`).

### Frontend (`frontend/src/`)
- `frontend/src/api.ts`:
  - Add API helpers for referral management, monetization metrics, and document exporting.
- `frontend/src/components/career/CareerScreen.tsx`:
  - Display subtle watermark indicator and non-intrusive upgrade prompt on Free exports.
  - Add "Invite a Friend" referral tab.
- `frontend/src/components/system/PricingModal.tsx`:
  - Update features listing to highlight watermark-free exports in paid tiers.

---

## 2. New Files

### Backend Core & Licensing
- `backend/app/licensing/watermark.py`:
  - Subtle markdown/HTML document watermarking module.
  - Text: `"Created with Saarthi • saarthi.ai"`.
- `backend/app/licensing/referral.py`:
  - Referral code generator and anti-abuse validation engine (self-referral check, device fingerprint matching).

### Tests
- `backend/tests/test_watermark_entitlements.py`
- `backend/tests/test_referral_system.py`
- `backend/tests/test_payment_reliability.py`
- `backend/tests/test_privacy_audit.py`

### Documentation (`backend/docs/`)
- `backend/docs/phase_s_implementation_plan.md`
- `backend/docs/phase_s_watermark_design.md`
- `backend/docs/phase_s_monetization_metrics.md`
- `backend/docs/phase_s_referral_design.md`
- `backend/docs/phase_s_privacy_audit.md`
- `backend/docs/phase_s_final_release_gate.md`

---

## 3. Database Changes
- **Referrals Table** (`referrals` in SQLite `data/saarthi.db` or dedicated licensing database):
  - `id` (INTEGER PRIMARY KEY)
  - `referrer_code` (TEXT UNIQUE)
  - `referrer_device_fingerprint` (TEXT)
  - `referee_device_fingerprint` (TEXT)
  - `status` (TEXT: PENDING, ACTIVATED, REWARDED, REJECTED)
  - `created_at` (TEXT)
  - `activated_at` (TEXT)

---

## 4. API Changes
- `POST /api/career/export-document`: Generates/exports a document (resume or cover letter) in Markdown/HTML format, applying watermark authoritatively if entitlement requires it.
- `GET /api/referral/code`: Retrieves or creates the user's unique referral code.
- `POST /api/referral/redeem`: Validates and redeems a referral code during signup/activation.
- `POST /api/payments/webhook`: Vendor payment gateway webhook handling (Razorpay HMAC-SHA256 signature verification).
- `GET /api/vendor/monetization-metrics`: Operational stats on watermark exposure, pricing views, checkouts, payment success, and referral conversions.

---

## 5. Frontend Changes
- **CareerScreen**:
  - Non-intrusive banner on Free tier exports: `"You're using Saarthi Free. Upgrade to remove the Saarthi watermark and unlock unlimited career tools."`
  - Export modal/button providing options for Markdown or HTML download.
  - "Invite a Friend" tab displaying referral link, code, and status.
- **PricingModal**:
  - Updated plan feature grid highlighting Watermark-Free PDF/Markdown exports.

---

## 6. Migration Strategy
1. Backward-compatible database schema addition (`CREATE TABLE IF NOT EXISTS referrals...`).
2. Entitlement model update defaults `requires_watermark = True` for existing unlicensed/Free users, ensuring zero breaking changes for existing paid tokens.
3. No modification to pre-existing user files on disk.

---

## 7. Rollback Strategy
1. Feature flag `ENABLE_WATERMARK` in `settings.py` can be set to `False` to immediately disable watermark injection across all endpoints.
2. Database additions are additive and non-destructive. Rollback requires zero schema drops.
