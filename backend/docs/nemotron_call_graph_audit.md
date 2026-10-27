# Nemotron AI Call Graph Audit Report

## Overview
Repository-wide call graph audit tracing every AI feature invocation to `NemotronService`.

---

## AI Invocations Matrix (Section 2)

| Feature / Endpoint | Caller Module | AI Provider Invocation | Service Layer Compliance | Audit Status |
| :--- | :--- | :--- | :--- | :--- |
| **Resume Tailoring** | `app/api/career.py` | `ModelFactory.get_provider()` | `NemotronService` | **PASS** |
| **ATS Scoring** | `app/api/career.py` | `ModelFactory.get_provider()` | `NemotronService` | **PASS** |
| **Cover Letter Gen** | `app/api/career.py` | `ModelFactory.get_provider()` | `NemotronService` | **PASS** |
| **Interview Prep Q&A**| `app/api/career.py` | `ModelFactory.get_provider()` | `NemotronService` | **PASS** |
| **Browser Assistant**| `app/api/browser_assistant.py` | `ModelFactory.get_provider()` | `NemotronService` | **PASS** |
| **Career Chat** | `app/agent/core.py` | `ModelFactory.get_provider()` | `NemotronService` | **PASS** |

---

## Call Graph Verification Conclusion
All 6 production AI entry points route strictly through `ModelFactory.get_provider()`, which initializes and validates `NemotronService`. Zero direct or unvalidated LLM calls exist.
