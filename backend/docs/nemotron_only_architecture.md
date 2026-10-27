# Saarthi Nemotron-Only AI Architecture Specification

## Overview
Technical design specification for Saarthi's strictly Nemotron-only local AI application architecture (`v0.5.0-rc2`).

---

## Architectural Principles (Sections 1, 4, 6)
1. **Single Approved Model**: NVIDIA Nemotron (`nemotron-3-nano:4b`) is locked as the ONLY production AI model across Saarthi.
2. **Central Service Layer**: All AI features (resume tailoring, ATS analysis, cover letter generation, interview prep, browser assistant) invoke `NemotronService` via `ModelFactory`.
3. **No Cloud Fallbacks**: Zero fallback to cloud LLM providers (OpenAI, Anthropic, Gemini, DeepSeek). If Nemotron is missing or offline, the system fails safely with structured recovery guidance.
4. **100% Private Local Execution**: Prompts, resumes, cover letters, and chat remain 100% local on the user's PC via Ollama.
