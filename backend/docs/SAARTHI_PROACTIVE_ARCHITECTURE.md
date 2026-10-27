# Saarthi Proactive & JARVIS Architecture

## Overview
Saarthi's Proactive Architecture provides situational awareness, proactive suggestion generation ("I noticed..."), rationale transparency ("Why Saarthi suggested this"), goal tracking, and routine automation.

## Proactive Suggestion Data Model (`ProactiveSuggestion`)
```json
{
  "id": "sugg_12345678",
  "title": "Job Description Requirement Extraction",
  "notice_text": "I noticed you loaded a new job description for Lead Security Architect.",
  "rationale": "Extracting hard requirements will improve your candidate evidence match score by 35%.",
  "action_type": "ASK",
  "target_domain": "career",
  "suggested_tool": "career.analyze_jd",
  "priority": "high",
  "status": "pending"
}
```

## Action Classification Levels
- **`IGNORE`**: Suppressed noise or previously dismissed suggestion pattern.
- **`SUGGEST`**: Non-intrusive card suggestion in UI.
- **`ASK`**: Requires explicit user confirmation before execution.
- **`ACT`**: Pre-authorized background routine execution.
