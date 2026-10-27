# Saarthi DomainPack & Routing Architecture

## Overview
Saarthi's Universal Domain Intelligence relies on pluggable `DomainPack` definitions managed by `DomainRegistry` and selected via `DomainRouter`.

## DomainPack Data Model (`DomainPack`)
```json
{
  "id": "cybersecurity",
  "name": "Cybersecurity & Audit",
  "description": "Security log audit, threat modeling, vulnerability analysis, and network artifacts.",
  "aliases": ["security", "infosec", "pentest", "audit"],
  "category": "technical",
  "system_instructions": "Conduct security analysis, identify vulnerabilities, and suggest remediations.",
  "allowed_tools": ["terminal.execute", "file.read", "browser.search"],
  "required_capability": "domain.cybersecurity"
}
```

## Router Decision Policy
1. **Explicit Lock**: User selection via `DomainPackSelector.tsx` or REST API overrides automatic routing (`confidence=1.0`).
2. **Project Domain Bias**: If active project has a primary domain, queries matching project keywords boost that domain.
3. **Intent Scoring**: Scored keyword matching assigns domain weights across 17 packs.
4. **General Fallback**: Default fallback to `general` companion.
