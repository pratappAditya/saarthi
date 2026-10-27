# Saarthi Cross-Domain Autonomy Architecture

## Overview
Saarthi is designed as **ONE universal AI operating companion**. The Cross-Domain Autonomy layer connects:
- **5A Entitlements** (FREE, STUDENT, PERSONAL, POWER, TEAMS, ENTERPRISE)
- **5B Intelligence Core** (Model Routing, Context Engine, Memory Manager)
- **5C Universal Assistant UX** (4 Experience Shells: Signature, Forge, Pulse, Aurora)
- **5D Agentic Execution** (TaskGraph Runtime, Dynamic Replanning, Approval Checkpoints)
- **5E Multimodal + Voice** (OCR, Vision, Audio, Hands-Free Voice)
- **5F Domain Intelligence** (Domain Packs & Domain Registry)
- **5G Proactive/JARVIS Intelligence** (Situational Awareness & Proactive Engine)
- **5H Advanced Voice** (Barge-in & Natural Directives)
- **5I Deep Personalization** (Context Precedence & Signal Learning)
- **5J Routines & Automation** (Triggered Workflows & Schedules)

---

## Architectural Principles

1. **Automatic Transition with Manual Lock**:
   - `DomainRouter.detect_domain_sequence()` identifies domain handoffs automatically.
   - Users can explicitly lock a domain (`explicit_domain`) when desired.

2. **Fact vs. Inference Strictness**:
   - Data passed between domains in a `DomainHandoff` payload is classified as `FACT` or `SOURCE-DERIVED`.
   - Analytical predictions remain `INFERENCE` to prevent model hypotheses from turning into immutable facts in downstream domains.

3. **Entitlement & Risk Governance**:
   - Every tool call evaluates plan capabilities (`FREE` through `ENTERPRISE`), domain permission, risk level (`low`, `medium`, `high`, `critical`), and human approval state.

4. **Four-Shell Parity**:
   - The cross-domain workflow engine operates on shared backend state. All four shells (`Signature`, `Forge`, `Pulse`, `Aurora`) render identical cross-domain data with shell-appropriate aesthetics.
