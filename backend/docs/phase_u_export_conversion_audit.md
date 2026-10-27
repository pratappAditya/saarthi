# Phase U Export Conversion & User Experience Audit

## Overview
Comprehensive technical audit tracing the user journey from resume generation, cover letter creation, export, watermark entitlement evaluation, upgrade prompt presentation, pricing modal interaction, payment activation, and clean document re-export.

---

## Technical Flow Tracing

### 1. Document Generation
- **Endpoints**: `POST /api/career/tailor-resume` and `POST /api/career/cover-letter`.
- **Entitlement Check**: Backend calls `default_client_manager.evaluate_license()`.
- **Watermark Decision**: If plan entitlement requires a watermark (`requires_watermark = True` for FREE plan), `WatermarkEngine.watermark_markdown()` appends `"Created with Saarthi • saarthi.ai"` to generated text.
- **Privacy Assurance**: Original imported user files on disk are **never** modified or watermarked.

### 2. Export & Seamless Re-Export (`POST /api/career/export-document`)
- **FREE User Behavior**: Exported content retains low-contrast watermark footer. Non-intrusive upgrade notice is returned alongside exported payload.
- **PAID User Behavior**: If user has upgraded to STUDENT, PERSONAL, POWER, or CUSTOM:
  - Backend authoritatively re-evaluates current active entitlement.
  - `WatermarkEngine.strip_watermark()` automatically removes any existing watermark footer text from previously generated documents.
  - Returns a clean, watermark-free document **without** requiring AI text re-generation.

### 3. Upgrade Notice & Pricing Modal Interaction
- **Trigger**: Non-intrusive banner appears upon generating/exporting documents on Free tier.
- **Pricing Modal**: Displays Student (₹149/mo), Personal (₹399/mo), Power (₹999/mo) plans.
- **Telemetry**: Logs `PRICING_VIEWED`, `UPGRADE_PROMPT_SHOWN`, `CHECKOUT_STARTED` without logging customer resume text.

### 4. Payment Activation & Race Condition Protection
- **Webhook Processing**: Razorpay/Stripe HMAC-SHA256 signature verification in `/api/payments/webhook`.
- **Activation Token**: License token is cached locally upon payment confirmation (`store_activation_token`).
- **Race Condition Invariant**: Legitimate payment immediately updates client manager state. If offline or delayed, offline grace period guarantees user is never forced to repurchase.

---

## Audit Findings & UX Assessment
1. **User Work Preservation**: Users **never** lose generated resume/cover letter content upon upgrading.
2. **Authoritative Authorization**: Frontend plan state is treated purely as UI display. Backend is 100% authoritative.
3. **No Dark Patterns**: Export is never hard-blocked. Free users can always download watermarked exports for immediate job search needs.
