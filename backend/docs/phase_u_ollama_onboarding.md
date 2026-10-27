# Phase U Local Ollama Onboarding & Diagnostics Optimization

## Overview
Technical documentation for local AI model diagnostic checks (`GET /api/ollama/diagnostics`), addressing the #1 user complaint ("Local model setup") while preserving 100% private, local-first workstation execution.

---

## Structured Diagnostic States

| State Code | Trigger Condition | Human-Readable Explanation | Recommended User Guidance | Can Retry? |
| :--- | :--- | :--- | :--- | :--- |
| **`READY`** | Port 11434 online & target model present | Local Ollama engine and model ready. | None | False |
| **`OLLAMA_NOT_INSTALLED`** | Connection refused on 127.0.0.1:11434 | Cannot connect to Ollama service. | Install from https://ollama.com and launch app. | True |
| **`MODEL_NOT_DOWNLOADED`** | Port online but `qwen2.5:3b` missing | Ollama is running but target model is missing. | Run `ollama pull qwen2.5:3b` in command line. | True |
| **`OLLAMA_OFFLINE`** | Port 11434 connection timeout | Ollama connection timed out. | Ensure Ollama desktop background service is running. | True |
| **`INSUFFICIENT_HARDWARE`** | Available RAM < 4.0 GB | Free system RAM is low. | Close unused heavy apps for smoother AI speed. | True |
| **`MODEL_CORRUPTED`** | Engine error loading weights | Model file error detected. | Re-download weights using `ollama pull`. | True |

---

## Privacy & Local Execution Guarantee
- Diagnostic endpoint runs **100% locally** on the user's PC.
- Zero chat messages, model prompts, or resume facts are transmitted to external servers during diagnostic checks.
