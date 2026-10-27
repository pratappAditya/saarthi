# SAARTHI — PHASE L.1 COMPLETE PRODUCT CAPABILITY AUDIT

**Date**: August 18, 2026  
**Baseline**: 2,171 backend tests, 1,091 adversarial tests, 24 live Ollama scenarios passing. Ed25519 Vendor licensing active.

---

## 1. Product Capability Matrix

| Feature | Status | Evidence | UX Completeness | Commercial Importance | Required Work |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Ollama** | IMPLEMENTED | [ollama.py](file:///e:/Saarthi/backend/app/models/ollama.py), [routes.py](file:///e:/Saarthi/backend/app/api/routes.py#L62-L117) | Functional, status check in Header & System Status Modal. | High | Add fallback & warning indicators when model service is offline. |
| **Chat** | IMPLEMENTED | [ChatCanvas.tsx](file:///e:/Saarthi/frontend/src/components/chat/ChatCanvas.tsx), [routes.py](file:///e:/Saarthi/backend/app/api/routes.py#L119-L165), [core.py](file:///e:/Saarthi/backend/app/agent/core.py) | Full chat UI, history SQLite persistence, session switching. | High | Integrate structured Career workspace so user doesn't rely solely on arbitrary chat prompts. |
| **Memory** | IMPLEMENTED | [sqlite.py](file:///e:/Saarthi/backend/app/memory/sqlite.py), [MemoryScreen.tsx](file:///e:/Saarthi/frontend/src/components/memory/MemoryScreen.tsx), [routes.py](file:///e:/Saarthi/backend/app/api/routes.py#L294-L316) | Approval cards, categories (FACT, PREFERENCE, PROJECT), search, delete. | High | Add career-specific memory tags and auto-memory extraction for user profile. |
| **Files** | IMPLEMENTED | [file_list.py](file:///e:/Saarthi/backend/app/tools/file_list.py), [file_read.py](file:///e:/Saarthi/backend/app/tools/file_read.py), [FilesScreen.tsx](file:///e:/Saarthi/frontend/src/components/files/FilesScreen.tsx) | File explorer, search, view inside allowed workspace root. | Medium | Add file upload parser for PDF/Docx/TXT resumes in Career Workspace. |
| **Terminal** | IMPLEMENTED | [terminal.py](file:///e:/Saarthi/backend/app/tools/terminal.py), [ToolsScreen.tsx](file:///e:/Saarthi/frontend/src/components/tools/ToolsScreen.tsx) | Execution with permission approval & risk assessment. | Medium | Restrict privileged terminal access on FREE and BASIC tiers via plan entitlements. |
| **Permissions** | IMPLEMENTED | [permissions.py](file:///e:/Saarthi/backend/app/security/permissions.py), [PermissionModal.tsx](file:///e:/Saarthi/frontend/src/components/permissions/PermissionModal.tsx) | Interactive confirmation dialog with risk levels & tool description. | Critical | Preserve all security contracts during Phase L UI/feature extensions. |
| **Sandbox** | IMPLEMENTED | [executor.py](file:///e:/Saarthi/backend/app/tools/executor.py), [settings.py](file:///e:/Saarthi/backend/app/config/settings.py) | `ALLOWED_ROOTS` boundary enforcement & path traversal protection. | Critical | Enforce local workspace isolation for all career uploads & drafts. |
| **Licensing** | IMPLEMENTED | [client_manager.py](file:///e:/Saarthi/backend/app/licensing/client_manager.py), [crypto.py](file:///e:/Saarthi/backend/app/licensing/crypto.py), [routes.py](file:///e:/Saarthi/backend/app/api/routes.py#L380-L421) | Ed25519 vendor-signed tokens, device binding, offline grace period. | Critical | Render active plan details, expiration date, and device status in UI settings. |
| **Vendor control plane** | PARTIALLY IMPLEMENTED | [vendor_server.py](file:///e:/Saarthi/backend/app/licensing/vendor_server.py) | Full backend SQLite engine (customers, licenses, devices, audit logs, CRL). UI operator missing. | Critical | Build a Vendor Control Center UI (desktop vendor operator view or route). |
| **Monthly plan** | IMPLEMENTED | [models.py](file:///e:/Saarthi/backend/app/licensing/models.py#L12), [vendor_server.py](file:///e:/Saarthi/backend/app/licensing/vendor_server.py#L126) | Backend enum & entitlement evaluation implemented. | High | Display pricing card (₹399/mo or $9.99/mo) in Plan UX. |
| **Yearly plan** | IMPLEMENTED | [models.py](file:///e:/Saarthi/backend/app/licensing/models.py#L13), [vendor_server.py](file:///e:/Saarthi/backend/app/licensing/vendor_server.py#L126) | Backend enum & entitlement evaluation implemented. | High | Display annual pricing card with discount in Plan UX. |
| **Student plan** | PARTIALLY IMPLEMENTED | [models.py](file:///e:/Saarthi/backend/app/licensing/models.py#L11) | Enum present in licensing models; dedicated career workspace & student verification missing. | Critical | Build Student Career Workspace, resume tailoring, and student eligibility flow. |
| **Free tier** | PARTIALLY IMPLEMENTED | [models.py](file:///e:/Saarthi/backend/app/licensing/models.py) | Licensing model evaluates default/trial entitlements; missing explicit FREE plan limits. | High | Add explicit FREE plan tier in backend models & enforce 3 job applications/month limit. |
| **Email** | NOT IMPLEMENTED | None | None | High | Build Email service / tool abstraction for drafting follow-ups & recruiter emails with explicit user confirmation. |
| **Calendar** | NOT IMPLEMENTED | None | None | High | Build Calendar service / tool abstraction for interview scheduling & follow-up reminders with explicit user confirmation. |
| **Resume import** | PARTIALLY IMPLEMENTED | [file_read.py](file:///e:/Saarthi/backend/app/tools/file_read.py) | Plain text file read via general tool; structured parser & profile extractor missing. | Critical | Create dedicated Resume Importer component & backend parser for text/markdown/PDF resumes. |
| **Resume tailoring** | NOT IMPLEMENTED | None | Unstructured chat prompting only. Dedicated workflow missing. | Critical | Build structured Resume Tailoring workspace distinguishing USER-PROVIDED FACT from AI SUGGESTION. |
| **Cover letter** | NOT IMPLEMENTED | None | Unstructured chat prompting only. Dedicated workflow missing. | Critical | Build Cover Letter Generator module in Career Workspace. |
| **ATS analysis** | NOT IMPLEMENTED | None | Unstructured chat prompting only. Dedicated scoring missing. | Critical | Implement ATS Keyword & Skill Match analysis engine in backend/frontend. |
| **Job application tracker** | NOT IMPLEMENTED | None | `TasksScreen.tsx` handles general tasks, not job applications. Database table missing. | Critical | Create `job_applications` SQLite table, FastAPI REST routes, and persistent Job Tracker Dashboard. |
| **Interview preparation** | NOT IMPLEMENTED | None | Unstructured chat prompting only. Dedicated interview mode missing. | High | Create dedicated Interview Preparation mode with role-specific Q&A, STAR format coaching, and mock interview. |
| **Application follow-up** | NOT IMPLEMENTED | None | None | High | Connect job tracker follow-up dates to email drafting & calendar event creation. |
| **Student verification** | NOT IMPLEMENTED | None | None | High | Build privacy-preserving student email (.ac.in / .edu) verification module. |
| **Payments** | IMPLEMENTED | [payment.py](file:///e:/Saarthi/backend/app/licensing/payment.py) | Backend PaymentProvider interface + Mock/Stripe/Razorpay providers. UI checkout missing. | High | Connect frontend billing UI to backend vendor payment activation endpoint. |
| **UPI** | PARTIALLY IMPLEMENTED | [payment.py](file:///e:/Saarthi/backend/app/licensing/payment.py#L91) | Razorpay backend provider supports UPI; frontend UPI checkout UI option missing. | Critical | Add explicit UPI checkout support in billing UI (configured for India hypothesis). |
| **Subscription management** | PARTIALLY IMPLEMENTED | [vendor_server.py](file:///e:/Saarthi/backend/app/licensing/vendor_server.py#L259) | Backend supports suspend, restore, renew, revoke, change entitlement. Frontend dashboard missing. | High | Build Subscription Management panel in Settings screen. |
| **Installer** | IMPLEMENTED | [saarthi_installer.iss](file:///e:/Saarthi/installer/saarthi_installer.iss), [windows_installer_validation.md](file:///e:/Saarthi/docs/windows_installer_validation.md) | Windows Inno Setup installer compiled & validated. | High | Ensure new career assets & DB schemas are preserved across updates. |
| **Onboarding** | IMPLEMENTED | [FirstRunOnboarding.tsx](file:///e:/Saarthi/frontend/src/components/onboarding/FirstRunOnboarding.tsx) | 3-step first-run wizard (Welcome, Security/Privacy, Ollama setup). | High | Add Student / Job-search persona selection step to onboarding. |
| **Privacy explanation** | IMPLEMENTED | [FirstRunOnboarding.tsx](file:///e:/Saarthi/frontend/src/components/onboarding/FirstRunOnboarding.tsx), [ARCHITECTURE.md](file:///e:/Saarthi/docs/ARCHITECTURE.md) | Explains local LLM execution & Ed25519 licensing telemetry scope. | Critical | Retain strict privacy guarantees: zero chat/resume/career telemetry to vendor. |

---

## 2. Summary of Gaps & Required Phase L Development

To transition Saarthi into a commercial product with the **Student Job-Search** wedge:

1. **Career / Job Search Workspace (Phase L.2 - L.3, L.6 - L.7)**:
   - SQLite `job_applications` table & FastAPI endpoints (`/api/career/*`).
   - Frontend `CareerScreen.tsx` with dedicated tabs:
     - **Dashboard**: Application tracker (SAVED, APPLIED, SCREENING, INTERVIEW, OFFER, REJECTED, WITHDRAWN) + analytics (Applications, Interviews, Offers, Response Rate).
     - **Resume & ATS Engine**: Resume import, target role matching, ATS keyword analysis, missing skills identification, and tailored resume generation (strictly separating USER FACT vs AI SUGGESTION).
     - **Cover Letter & Outreach**: Dedicated tailored cover letter builder.
     - **Interview Prep**: Job-specific questions, technical/behavioural practice, STAR coaching, and feedback.
2. **Email & Calendar Integrations (Phase L.4 - L.5)**:
   - Email drafting engine (Recruiter follow-up, thank you notes, application follow-up) with **EXPLICIT USER CONFIRMATION** dialog before sending/exporting.
   - Calendar scheduling engine (.ics generation & reminder creation for interviews/follow-ups) with **EXPLICIT USER CONFIRMATION**.
3. **Plan Entitlements & Pricing UX (Phase L.8 - L.10)**:
   - Commercial plan hierarchy in backend: FREE, STUDENT, PERSONAL, POWER, CUSTOM.
   - Configurable India pricing hypothesis (Student: ₹149/mo, Personal: ₹399/mo, Power: ₹999/mo).
   - FREE tier limits (3 job applications/month, basic local chat, memory, files, no privileged terminal).
   - Privacy-safe Student eligibility verification via `.ac.in` / `.edu` email domain check.
4. **Vendor Control Center & Billing (Phase L.11 - L.12)**:
   - Private Vendor Control Center interface in frontend (accessible via secret key/admin route) allowing full management of customers, licenses, activations, suspensions, renewals, CRL, and audit logs.
   - Payment checkout UI supporting Razorpay / UPI / Cards connected to backend `PaymentProvider` factory.
5. **Privacy UX & Security Audit (Phase L.13 - L.15)**:
   - Transparent privacy breakdown of what stays local (all chat, resumes, applications, memory) vs what leaves (Ed25519 licensing telemetry).
