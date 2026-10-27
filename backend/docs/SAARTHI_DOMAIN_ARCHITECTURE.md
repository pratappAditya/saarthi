# Saarthi Multi-Domain Pack Architecture

## Overview

Saarthi is designed as a multi-domain personal AI operating companion. The Career Workspace is the **first domain pack**, serving as the baseline template for future domain packs.

## DomainPack Interface

```typescript
export interface DomainPackConfig {
  id: string;              // e.g. "domain.cybersecurity"
  name: string;            // e.g. "Cybersecurity & Pentesting Suite"
  category: string;        // e.g. "Security"
  description: string;
  minimum_plan: PlanId;    // e.g. "power"
  capabilities: string[];  // e.g. ["domain.cybersecurity", "tools.terminal"]
  tools: string[];         // e.g. ["tools.terminal", "tools.files"]
  icon: string;
  is_active: boolean;
  is_installed: boolean;
}
```

## Available Domain Packs

1. **`domain.career`**: Career Operating Workspace (Master resume, truthful tailoring, ATS, interview prep, salary coach).
2. **`domain.education`**: Education & Study Companion (Flashcards, course notes, paper summaries, guided study).
3. **`domain.writing`**: Writing & Content Studio (Long-form writing, technical docs, essay drafting, proofreading).
4. **`domain.general`**: General AI Companion (Daily planning, quick Q&A, general assistance).
5. **`domain.business`**: Business & Entrepreneurship (Market research, financial analysis, strategy).
6. **`domain.engineering`**: Engineering & Systems Workbench (CAD data inspection, systems design, calculation).
7. **`domain.software`**: Software Development IDE Pack (Code generation, Git integration, bug fixing, test suite automation).
8. **`domain.cybersecurity`**: Cybersecurity & Pentesting Suite (PCAP analysis, threat triage, vulnerability scanning, OWASP audits).
9. **`domain.science`**: Biomedical & Life Sciences Suite (PubMed query workflows, protein sequence inspection, literature synthesis).
10. **`domain.research`**: Academic Research Pack (arXiv/EuropePMC paper search, multi-source literature synthesis, LaTeX).
