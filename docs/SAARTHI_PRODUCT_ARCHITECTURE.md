# Saarthi Phase 6 Product Architecture Specification

Saarthi is designed as **ONE universal AI operating companion**. 

## Unified Subsystem Architecture

1. **Entitlements & Gating**: Server-side authorization via `require_capability` enforcing plan matrix (`free`, `student`, `personal`, `power`, `teams`, `enterprise`).
2. **Intelligence Core**: Hybrid router supporting local Nemotron/Ollama models, OpenRouter, and fallback providers.
3. **Universal UI Shells**: Signature, Forge, Pulse, and Aurora experience shells representing presentation modes over one state.
4. **Agentic Task Engine**: Autonomous `TaskGraph` planner executing sequential/parallel steps with human permission checkpoints.
5. **Document & Research Engine**: OCR, PDF/DOCX ingestion, arXiV/EuropePMC multi-query literature synthesis, and citation provenance.
6. **Universal Domain Registry**: 17 specialized domain packs registered in `DomainRegistry`.
7. **Proactive / JARVIS Engine**: Situational awareness, next-action recommendation, quiet hours, and routine automation.
8. **Admin Control Plane**: Privileged operational control plane for users, plans, entitlements, feature flags, telemetry, backups, and beta feedback.
