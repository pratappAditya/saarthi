# Phase 5I — Deep Personalization Manual QA Protocol

## Pre-requisites
1. Start Saarthi backend: `uvicorn main:app --reload`
2. Start Saarthi frontend: `npm run dev`

---

## Test Scenario 1: Deep Personalization Dashboard
1. Open Saarthi and press `Ctrl+K` -> **Open Deep Personalization Dashboard**.
2. Verify Dashboard displays:
   - Communication Style, Technical Depth, Proactivity Level, and Learned Inferences.
   - Tabs: Learned Preferences, Communication & Work Controls, Domain Expertise Model, Privacy Toggles.

---

## Test Scenario 2: Explicit Communication & Work Control Updates
1. Navigate to **Communication & Work Controls** tab.
2. Change Communication Style to `Executive Briefing` and Response Length to `Concise`.
3. Send a message in Command Center.
4. Verify Saarthi adapts output format to a direct, concise executive summary.

---

## Test Scenario 3: What Saarthi Knows About Me Inspector
1. Navigate to **Learned Preferences** tab.
2. Click **Inspect Provenance** on an inferred preference item.
3. Verify modal displays:
   - Source (`MODEL_INFERRED` / `USER_CONFIRMED`), Confidence %, Evidence provenance string, Affected behavior, Timestamps.
4. Click **Confirm Fact** or **Reject Fact** and verify preference status updates.

---

## Test Scenario 4: Domain Expertise Matrix Adaptation
1. Navigate to **Domain Expertise Model** tab.
2. Set `cybersecurity` domain level to `EXPERT`.
3. Ask a cybersecurity query: `"Analyze network telemetry logs."`
4. Click **Explain Personalization** in `Ctrl+K` menu or check response context.
5. Verify Saarthi adapts to expert depth, skipping basic introductory setup explanations.

---

## Test Scenario 5: Precedence Order Hierarchy
1. Set Global response length to `Concise`.
2. Open a project workspace with Project Override set to `Detailed`.
3. Submit a query without explicit turn prompt override; verify response is detailed.
4. Submit a turn prompt explicitly requesting "concise overview"; verify Task Prompt Override takes highest precedence.

---

## Test Scenario 6: Personalization Privacy & Learning Toggles
1. Navigate to **Privacy & Learning Toggles** tab.
2. Toggle **Enable Behavioral Learning** to `OFF`.
3. Execute repeated tool actions; verify no new inferred preferences are added.
4. Click **Reset All Personalization Data**; confirm profile resets to default baseline cleanly.
