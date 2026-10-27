# Memory Contract Architecture Specification

## Overview
This document formalizes memory creation, secret screening, approval workflow, persistence, relevance scoring, and retrieval context injection.

---

## Memory Pipeline Lifecycle

```
User Message
→ Secret Screening (rejection of passwords, API keys, tokens)
→ Memory Detection / Suggestion (`suggest_memory` or explicit command)
→ Memory Request Card (`MemoryRequest`)
→ User Approval / Denial Workflow
→ Exactly-Once Persistence in SQLite Memory
→ Relevance Scoring & Context Ranking
→ Model System Prompt Context Injection
```

---

## Scoring & Ranking Specifications

Candidate memories are scored using:
- **Exact Key Match**: +10 points
- **Content String Match**: +5 points
- **Keyword Matches**: +2 to +3 points per matching word
- **Category Context Boost**: +5 points for category relevance (e.g. `PREFERENCE` / `PROJECT`)
- **Metadata Confidence Weight**: +5 * confidence

Top memories are truncated to fit context limits (`MAX_MEMORY_CONTEXT_CHARS`, default 2000 chars; `MAX_MEMORY_RESULTS`, default 5).

---

## Secret Screening Contract
- User input and memory creation MUST screen for API keys, passwords, bearer tokens, private SSH keys, and connection strings.
- Detected secrets MUST be rejected before persistence.
