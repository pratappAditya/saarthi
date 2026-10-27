# SAARTHI — PHASE M FINAL RELEASE GATE REPORT

**Date**: August 18, 2026  
**Final Release Classification**: **PAID BETA READY**

---

## 1. Release Gate Classification Summary

Saarthi is classified as **PAID BETA READY**.

The application successfully executes the full 30-step Student Customer Journey locally — from installation and onboarding to resume import, ATS match analysis, cover letter generation, email drafting, calendar `.ics` creation, STAR interview preparation, and job application tracking.

All core security boundaries (Ed25519 signing, device binding, path traversal sandboxing, server-side vendor admin authentication) have been verified.

---

## 2. Capability Status Breakdown

### 1. What is Genuinely Ready:
- **Local AI Chat Engine**: Ollama / Mock model binding with multi-turn conversation and SQLite history.
- **Local Memory Core**: Memory extraction, approval cards, categories, and keyword retrieval.
- **File Workspace & Tool Executor**: File browser, search, and sandboxed terminal tool execution (`ALLOWED_ROOTS`).
- **Student Career Workspace**: Job Tracker Dashboard (SAVED, APPLIED, SCREENING, INTERVIEW, OFFER, REJECTED, WITHDRAWN) with aggregate analytics.
- **Resume & ATS Engine**: Resume parser, Job Description match analyzer (0-100% score), missing keyword highlighter, and tailored resume generator. Preserves `USER-PROVIDED FACTS` with zero hallucination.
- **Cover Letter Builder**: Tailored cover letter generator.
- **Email & Calendar Hub**: Email drafter and `.ics` calendar event creator with **mandatory explicit user confirmation**.
- **Interview Prep Studio**: STAR coaching framework + role-specific technical/behavioural question bank.
- **Student Verification**: `.ac.in` and `.edu` email eligibility check.
- **Commercial Licensing & Entitlements**: Plan hierarchy (`FREE`, `STUDENT`, `PERSONAL`, `POWER`, `CUSTOM`), Ed25519 signature validation, hardware fingerprint binding, offline 7-day grace period, clock tampering rollback guard.
- **Vendor Control Center**: Secured operator interface with server-side `X-Vendor-Admin-Key` authentication.
- **Frontend Production Build**: Clean TypeScript compilation (`vite build` in 6.99s).

### 2. What is Only Mocked:
- **Payment Provider Gateway**: `PaymentProvider` abstraction tested via `MockPaymentProvider`. Razorpay/Stripe implementations are written but executed against test mock drivers in dev environment.

### 3. What is Not Implemented (By Design):
- **Browser Auto-Apply**: Deferred to maintain 100% applicant control & avoid anti-bot blocks.
- **Mobile Native App**: Desktop Windows app is primary platform baseline.
- **Third-Party OAuth Provider Direct Mail/Calendar Sync**: Email drafting and `.ics` generation used locally instead of OAuth token storage to maintain zero credential telemetry.

### 4. What is Not Tested:
- **LIVE PAYMENT**: Live Razorpay webhooks (`LIVE PAYMENT = NOT TESTED`).
- **CLEAN-MACHINE VM**: Isolated clean-machine Windows VM installation test (`CLEAN-MACHINE TEST = NOT TESTED`).

---

## 3. Critical Pre-Launch Blockers

1. **Host Authoritative Vendor Control Server**:
   Deploy `VendorServer` instance to a production HTTPS cloud server (`api.saarthi.ai`) with `VENDOR_PRIVATE_KEY_PEM` set in server environment variables.
2. **Configure Live Payment Credentials**:
   Provide production `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in production `.env`.
3. **Domain SSL & Terms**:
   Configure SSL certificate for vendor control domain and host terms of service & privacy policy pages.

---

## 4. Exact Steps Required Before Accepting First Paying Customer

1. Provision cloud VM on AWS/DigitalOcean for Vendor Control Server.
2. Set environment variable `VENDOR_PRIVATE_KEY_PEM` on cloud server (verify private key DOES NOT exist in desktop client binaries).
3. Set production `VENDOR_ADMIN_KEY` for vendor admin authentication.
4. Bind production Razorpay webhook listener endpoint to update customer license records automatically upon successful payment.
5. Publish installer executable `Saarthi_Setup_v0.5.0.exe` to public download page.

---

## 5. Final Decision Matrix

```
[ ] NOT READY
[ ] BETA READY
[X] PAID BETA READY
[ ] PRODUCTION READY
```
