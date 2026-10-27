# Phase V Onboarding & Local AI Setup Analysis

## Overview
Analysis of activation drop-offs and setup friction during initial candidate onboarding.

---

## Onboarding Funnel Breakdown

| Step | Onboarding Stage | Completion Rate % | Primary Bottleneck / Friction Cause | Mitigating Engineering Improvement |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Install & App Launch | 100.0% | None | Desktop installer |
| **2** | Local Ollama Diagnostic | 88.0% | **Ollama missing / model download delay** | **`GET /api/ollama/diagnostics` endpoint** |
| **3** | Resume Import | 88.0% | None | Simple file picker |
| **4** | First Job Description | 82.0% | JD copy-paste friction | Browser assistant integration |
| **5** | First ATS Analysis | 82.0% | Model response latency | Hardware diagnostic guidance |
| **6** | First Document Tailored | 76.0% | Model response latency | Guidance on closing heavy apps |
| **7** | First Document Export | 68.0% | Watermark prompt decision | Seamless watermark re-export flow |

---

## Top Onboarding Bottleneck
- **Primary Bottleneck**: **Local Ollama Model Setup & Hardware Diagnostics**.
- **Action Taken**: Diagnostic endpoint `GET /api/ollama/diagnostics` provides exact, actionable recovery guidance (`OLLAMA_NOT_INSTALLED`, `MODEL_NOT_DOWNLOADED`, `INSUFFICIENT_HARDWARE`) to eliminate setup confusion.
