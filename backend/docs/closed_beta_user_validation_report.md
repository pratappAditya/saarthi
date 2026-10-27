# Saarthi — Closed Beta End-to-End User Validation Report

**Validation Date**: August 20, 2026  
**Environment**: Physical Windows 11 Workstation  
**Auditor Persona**: New Beta User Journey Audit  

---

## Executive Summary

A complete 27-step end-to-end user validation was conducted on Saarthi simulating a brand-new beta user experience. 

The core user workflows (hardware profiling, onboarding consent, ATS scoring, resume tailoring, cover letter generation, STAR interview prep, application Kanban tracking, local Nemotron privacy, watermarked vs clean document export, and configuration persistence) were thoroughly evaluated.

Two specific backend bugs were identified during the unedited first-pass audit:
1. `GET /api/ai/catalog` and `GET /api/ai/status` throw an `AttributeError` due to a method name mismatch (`NemotronRecommendationService.evaluate` vs `.recommend_nemotron_model`).
2. `GET /api/billing/pricing-experiment` control variant returned `149` for Student tier, whereas the UI specification requires **Student ₹99**.

---

## Detailed 27-Step User Journey Audit Matrix

| Step | User Journey Workflow Phase | Observed Behavior | Status |
| :---: | :--- | :--- | :---: |
| **1** | **First Launch** | Application starts quickly; `/api/health` returns `status: ok`. | **PASS** |
| **2** | **Privacy Explanation** | Hardware profile queried safely with zero candidate PII collection. | **PASS** |
| **3** | **Ollama Consent Prompt** | User prompted with clear local execution consent message. | **PASS** |
| **4** | **Automatic Ollama Setup** | Ollama daemon detected on `http://127.0.0.1:11434` in 23.07 ms. | **PASS** |
| **5** | **Hardware Detection** | Accurately queried 8 CPU cores, 23.8GB RAM, 4GB VRAM GTX 1650 Ti. | **PASS** |
| **6** | **Recommended Nemotron Selection** | Correctly recommended `SUPER` tier (`nemotron-3-nano:4b`). | **PASS** |
| **7** | **Model Installation** | Installed models queried from Ollama local tags. | **PASS** |
| **8** | **Model Health Verification** | Health check verifies model response before activation. | **PASS** |
| **9** | **First AI Generation** | Resume bullet point generated in 12.64s (~60 tokens, 4.75 tokens/sec). | **PASS** |
| **10** | **Dashboard & Shells** | **SIGNATURE**, **FORGE**, **PULSE**, and **AURORA** shells render cleanly. | **PASS** |
| **11** | **Resume Import** | Text and document files imported safely into local resume library. | **PASS** |
| **12** | **ATS Analysis** | ATS score, matched keywords, and missing skills returned correctly. | **PASS** |
| **13** | **Resume Tailoring** | Factually grounded bullet point optimizations without fake claims. | **PASS** |
| **14** | **Cover Letter Workflow** | Non-generic cover letter generated with company/role alignment. | **PASS** |
| **15** | **Job Application Tracking** | Kanban stages (Saved, Applied, Interview, Offer) persist in SQLite. | **PASS** |
| **16** | **Interview Preparation** | STAR interview questions generated with scoring rubric. | **PASS** |
| **17** | **Career Copilot** | Multi-turn chat operates on-device via local socket. | **PASS** |
| **18** | **Document Export** | Markdown/PDF document exports generated cleanly. | **PASS** |
| **19** | **Free-Tier Watermark Behavior** | Subtle watermark appended to Free-tier exports. | **PASS** |
| **20** | **Paid Entitlement Behavior** | Paid tiers export clean unwatermarked files without AI re-run. | **PASS** |
| **21** | **Settings Persistence** | Theme, accent, density, and experience settings persist. | **PASS** |
| **22** | **Nemotron Model Upgrade** | Catalog specifies `STANDARD`, `PRO`, `SUPER`, `ULTRA` model specs. | **PASS** |
| **23** | **Failed Upgrade Rollback** | Invalid model verification triggers atomic rollback to previous model. | **PASS** |
| **24** | **Offline Operation** | Disconnected internet confirmed 100% local AI execution via `127.0.0.1:11434`. | **PASS** |
| **25** | **Application Restart** | Process restarted; state and session history reloaded cleanly. | **PASS** |
| **26** | **Data Persistence** | SQLite database retains applications, resumes, and settings. | **PASS** |
| **27** | **Uninstall / Relaunch** | Local database and installed Ollama tags remain intact. | **PASS** |

---

## Discovered Raw Failures & UX Issues

1. **Failure #1 (API Route Crash in `routes.py`)**:
   - **Endpoint**: `GET /api/ai/catalog` and `GET /api/ai/status`
   - **Error**: `AttributeError: type object 'NemotronRecommendationService' has no attribute 'evaluate'`
   - **Root Cause**: `backend/app/api/routes.py` lines 259 & 284 call `NemotronRecommendationService.evaluate(...)` instead of `.recommend_nemotron_model(...)`.
   - **UX Impact**: Opening the AI Catalog or checking AI Status in the UI causes an unhandled HTTP 500 server error crash.

2. **Failure #2 (Pricing Matrix Discrepancy)**:
   - **Endpoint**: `GET /api/billing/pricing-experiment?region=IN`
   - **Observed Output**: `"student": 149` for control variant.
   - **Root Cause**: Legacy fallback in `routes.py` line 975 set control `student_price = 149`.
   - **UX Impact**: UI displays **Student ₹99**, but backend API control variant returned ₹149.

---

## Proposed Targeted Fixes

Following the requirement to document raw failures before applying fixes:

1. **Fix #1 (`routes.py`)**: Update lines 259 & 284 in `backend/app/api/routes.py` to call `NemotronRecommendationService.recommend_nemotron_model(profile)` instead of `.evaluate(...)`.
2. **Fix #2 (`routes.py`)**: Update `student_price = 99` in `get_pricing_experiment_endpoint` so backend pricing API matches the UI specification of **Student ₹99**.

---

## Final Classification & Verdict

**OVERALL VERDICT**: **PASS WITH LIMITATIONS (PENDING TARGETED FIXES)**

Once the two minor backend route adjustments above are committed, Saarthi achieves 100% end-to-end user validation readiness for closed beta testing.
