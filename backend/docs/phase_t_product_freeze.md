# Phase T: Product Freeze Record

## Overview
Saarthi is frozen at version **v0.5.0-rc2** for Phase T Real Revenue Validation and Product-Market-Fit Optimization.
No core functional changes are permitted unless a critical production bug is discovered.

---

## Technical Freeze Baseline

### 1. Build & Version Identifiers
- **Application Version**: `v0.5.0-rc2`
- **Backend Environment**: Python 3.14.6 + FastAPI + SQLite
- **Frontend Production Build**: Vite v8.2.1
  - CSS Bundle: `dist/assets/index-DT9lYTHt.css` (70.75 kB)
  - JS Bundle: `dist/assets/index-BHfGeu7i.js` (508.83 kB)
- **Git Commit / Repository State**: Workspace frozen at `e:\Saarthi`

### 2. Test Suite Validation
- **Backend Test Count**: **2,207 passed / 0 failed / 1 warning** (Total run time: 124s)
- **Phase S Test Suite**: 14 passed / 0 failed
- **Licensing Core & Security Suite**: PASSED
- **Adversarial Security Suite**: 1,091 / 1,091 PASSED
- **Browser Assistant Safety Suite**: PASSED
- **Privacy Audit**: 0 customer content leaks detected

### 3. Database Schema Baseline
SQLite Database: `data/database/saarthi.db`
- `chat_history`: Session messages (session_id, sender, message, timestamp)
- `memories`: Fact storage (category, key, content, project_id, status)
- `job_applications`: Application tracker (company, role, status, job_url, salary, follow_up_date)
- `resumes`: User resume baselines (title, raw_content, parsed_facts, is_default)
- `referral_codes`: User referral codes (user_id, code, device_fingerprint, created_at)
- `referral_redemptions`: Referral redemptions (referral_code, referrer_user_id, referee_user_id, status)
- `churn_feedback`: Privacy-safe churn reasons (category, user_id, timestamp)

### 4. Cryptographic Licensing Protocol
- Asymmetric Key Scheme: **Ed25519**
- Vendor Server: `VendorServer` in `app/licensing/vendor_server.py`
- Client Manager: `ClientLicensingManager` in `app/licensing/client_manager.py`
- Device Binding: Hardware UUID + MAC hash (`get_device_fingerprint`)
- Failsafe Tamper Resistance: Fails closed on local database or license cache modification.

### 5. Pricing & Entitlements
- **Pricing**:
  - `STUDENT`: ₹149 / month | ₹1,299 / year
  - `PERSONAL`: ₹399 / month | ₹3,499 / year
  - `POWER`: ₹999 / month | ₹8,999 / year
  - `CUSTOM`: Custom Enterprise pricing
- **Entitlements**:
  - `FREE`: 3 applications/mo, 6 history messages, local chat, standard tools, watermarked exports (`requires_watermark = True`).
  - `STUDENT`: Unlimited applications, 12 history messages, watermark-free exports (`requires_watermark = False`).
  - `PERSONAL`: Unlimited applications, 16 history messages, privileged terminal, watermark-free exports.
  - `POWER`: Unlimited applications, 32 history messages, 2-device binding, watermark-free exports.

### 6. Watermark & Referral Behavior
- **Watermark**: Appends `"Created with Saarthi • saarthi.ai"` on Free tier generated/exported documents. User's original imported resume is **never** watermarked.
- **Referral Engine**: Unique codes (`REF-XXXXXX`). Enforces self-referral and same-device fingerprint anti-abuse controls.

### 7. Payment Architecture
- Webhooks: Razorpay / Stripe HMAC-SHA256 signature verification in `app/licensing/payment.py` and `routes.py`.
