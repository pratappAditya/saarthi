# Saarthi Phase 5 Final Architecture Specification

## Overview
Saarthi is **ONE universal AI operating companion**. The complete Phase 5 architecture integrates 11 specialized sub-layers into a single, cohesive local-first intelligence operating engine.

---

## Core System Diagram

```
USER INPUT (Text, Voice, PDF, Image, Audio)
                │
                ▼
    Multimodal Attachment Engine
                │
                ▼
      ContextBundle Assembler
   (Task > Project > Domain > Global)
                │
                ▼
     Deep Personalization Engine
                │
                ▼
        DomainRouter Sequence
  (Archaeology -> History -> Research -> Writing)
                │
                ▼
       TaskGraph Planner Engine
                │
                ▼
      Entitlement Check (5A)
(FREE / STUDENT / PERSONAL / POWER / TEAMS / ENTERPRISE)
                │
                ▼
     Permission Engine & Risk Policy
                │
                ▼
      Multi-Domain Agent Execution
                │
                ▼
        Domain Handoff System
 (Verified Facts vs. Model Inferences)
                │
                ▼
      Trust & Audit Logging Core
                │
                ▼
    Proactive Next Action Dispatcher
                │
                ▼
     Output Generation (Text / Voice / UI)
                │
                ▼
 Durable Memory & Project / Goal Updates
```

---

## Security & Local-First Sandbox

- **Data Boundary**: 100% of user data, resumes, project artifacts, research papers, and memories remain strictly local on disk in SQLite (`%LOCALAPPDATA%\Saarthi\saarthi.db`).
- **Prompt Injection Defense**: Uploaded documents are parsed strictly as passive DATA, never as executable model instructions.
- **Human Approval Checkpoints**: High-risk tool calls (`medium`, `high`, `critical`) trigger confirmation prompts prior to execution.
