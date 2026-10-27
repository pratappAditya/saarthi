# Saarthi Integration and Design System Reference Guide

This guide documents the layout, custom state logic, and branding accents implemented during the integration of the AI Studio-designed user interface.

## Branding Accents and Accents

Saarthi utilizes a premium dark mode layout inspired by modern terminal setups and developer dashboards:
- **Primary Background:** Solid deep pitch black (`#0A0A0A`).
- **Surface Panels:** Matte dark charcoal (`#0D0D0D` and `#141414`).
- **Accents:** Vivid saffron amber glow (`#F59E0B`), used for active navigation pills, the central intelligence orb states, memory headers, and highlight capsules.
- **Visuals:** High-fidelity micro-animations for state changes via the `motion` package.

## Component States

1. **Idle / Listening State:** Central saffron orb pulses gently.
2. **Thinking State:** Orb rotates with sub-animations, signaling that the local LLM is parsing text and evaluating contexts.
3. **Tool Execution State:** Saffron warning borders activate on active card containers, detailing parameters in collapsible JSON blocks.
4. **Suspended Permission State:** A modal overlay interrupts user operations, forcing an explicit allow/deny decision for shell script executions or file deletions.

## API Binding Endpoints

FastAPI provides the following endpoint structure connected to our centralized `api.ts` frontend module:

| Endpoint | Method | Purpose | UI Integration |
| :--- | :--- | :--- | :--- |
| `/api/status` | GET | System hardware diagnostic data | Renders CPU, GPU loading details in settings modal & sidebar footers |
| `/api/chat` | POST | Submits user messages to AgentCore | Appends message thread; processes tools and permission suspensions |
| `/api/history/{sess_id}` | GET | Fetches conversation threads | Loads history on browser startup |
| `/api/history/{sess_id}` | DELETE | Deletes current chat thread | Triggered by the general settings clear history button |
| `/api/permissions/pending` | GET | Check for pending security actions | Pops the security consent modal overlay |
| `/api/permissions/{id}/approve` | POST | Grant execution approval | Resumes suspended agent steps |
| `/api/permissions/{id}/deny` | POST | Deny execution approval | Resume loop with a denial exception payload |
| `/api/memory` | GET | Retrieves active stored facts | Populates local facts dashboard screens |
| `/api/memory/{id}` | DELETE | Forgets a specific fact | Removes memory card from DB store |
| `/api/memory/approve/{id}` | POST | Approve fact save suggestion | Saves fact into local permanent SQLite database |
| `/api/memory/deny/{id}` | POST | Reject memory suggestion | Closes inline card suggestions in chat bubbles |
