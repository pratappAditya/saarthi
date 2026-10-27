# SAARTHI — PHASE N PAID BETA LAUNCH & REAL CUSTOMER VALIDATION REPORT

**Date**: August 18, 2026  
**Auditor**: Antigravity AI Engineering Team  
**Final Release Classification**: **PAID BETA ACTIVE**

---

## 1. Release Classification & Beta Overview

Saarthi is officially transition into **PAID BETA ACTIVE** mode.

The product baseline is frozen at `v0.5.0-rc2`. The primary focus is now **controlled real-world validation** with 10–20 selected beta users (final-year university students, fresh graduates, and active job seekers) using the Student Career Workspace wedge.

---

## 2. Capability & Audit Matrix

| Category | Status | Details |
| :--- | :--- | :--- |
| **Product Baseline** | FROZEN | Application `v0.5.0-rc2`, Vite build `index-BbgREu3g.js`, SQLite v3 schema. |
| **Tested Capabilities** | TESTED | Local AI chat, SQLite memory, sandboxed terminal tools, Career Workspace, ATS match analyzer, cover letter builder, STAR interview prep, email drafter, `.ics` calendar generator, `.ac.in` student verification, Ed25519 token signatures, hardware device binding, offline grace period, clock rollback guard, server-side vendor admin auth (`X-Vendor-Admin-Key`). |
| **Simulated Capabilities** | SIMULATED | `PaymentProvider` abstraction tested via `MockPaymentProvider` in dev environment. |
| **Untested Capabilities** | UNTESTED | Live production Razorpay webhook processing (`LIVE PAYMENT = NOT TESTED`) & clean isolated Windows VM installation (`CLEAN-MACHINE TEST = NOT TESTED`). |
| **Vendor Control Server** | READY | `VendorServer` engine active with server-side admin authentication and Ed25519 private key isolation. |
| **Installer Executable** | READY | Inno Setup `Saarthi_Setup_v0.5.0.exe` compiled and ready for beta distribution. |
| **Customer Journey** | VERIFIED | Complete 30-step flow from download to persistent career workspace execution verified. |
| **Security & Privacy** | VERIFIED | `PrivacySafeTelemetryLogger` active; zero customer prompts, chat messages, resumes, or secrets logged. |

---

## 3. Controlled Beta Strategy (10–20 Users)

### Beta Target Cohort:
- 10–20 final-year engineering/university students and fresh graduates in India actively searching for software/tech roles.

### Beta Package Deliverables per User:
1. `Saarthi_Setup_v0.5.0.exe` installer download link.
2. Student plan onboarding key (₹149/mo hypothesis).
3. Student email verification check (`.ac.in` / `.edu`).
4. Support contact: `support@saarthi.ai`.
5. Beta feedback form link.

---

## 4. Privacy-Safe Product Metrics Tracking (N.9 & N.11)

The following operational metrics are tracked with **ZERO customer content logging**:
- **Activation Rate**: Ratio of successful key activations to issued tokens.
- **Payment Success Rate**: Razorpay checkout conversion rate.
- **First-Session Completion**: Onboarding wizard completion rate.
- **Career Workspace Adoption**: Percentage of users creating 1+ job application records.
- **7/14/30-Day Retention**: Percentage of active users returning in subsequent weeks.
- **Support Incidents**: Logged via customer support SOP workflow ([customer_support_sop.md](file:///e:/Saarthi/backend/docs/customer_support_sop.md)).

---

## 5. Beta Pricing Hypothesis (N.13)

| Plan | Monthly Price | Yearly Price | Features & Entitlements |
| :--- | :--- | :--- | :--- |
| **STUDENT** | ₹149 / mo | ₹1,299 / yr | Unlimited job applications, ATS match analyzer, cover letter builder, interview prep studio, 1 device. |
| **PERSONAL** | ₹399 / mo | ₹3,499 / yr | Unlimited applications, basic tools + terminal access, 1 device. |
| **POWER** | ₹999 / mo | ₹8,999 / yr | Unlimited applications, advanced tools, 32k context, 2 bound devices. |

---

## 6. Non-Negotiable Operational Boundaries (N.12)

The following features are **EXPLICITLY FORBIDDEN** from being added during Phase N:
- ❌ NO browser auto-apply engines.
- ❌ NO native mobile applications.
- ❌ NO arbitrary AI feature bloat.
- ❌ NO third-party OAuth direct email sending (local email drafting & `.ics` export only).

---

## 7. Final Classification Decision Matrix

```
[ ] BETA NOT READY
[X] PAID BETA ACTIVE
[ ] PAID BETA SUCCESSFUL
[ ] READY FOR PUBLIC LAUNCH
```
