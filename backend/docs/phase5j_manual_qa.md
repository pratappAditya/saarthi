# Phase 5J — Routines & Automation Manual QA Protocol

## Pre-requisites
1. Start Saarthi backend: `uvicorn main:app --reload`
2. Start Saarthi frontend: `npm run dev`

---

## Test Scenario 1: Natural Language Routine Creation & Preview
1. Open Saarthi and press `Ctrl+K` -> **Create New Automation Routine**.
2. Type prompt: *"Every Monday at 9 AM review my active projects and tell me what needs attention"*.
3. Click **Parse Routine**.
4. Verify structured preview displays name, schedule, actions, autonomy level, and approval policy.
5. Click **Activate Routine** and verify it appears in Active Routines list.

---

## Test Scenario 2: Visual Routine Builder
1. In Routines Hub, click **+ Create New Routine** -> **Visual WHEN/IF/THEN** tab.
2. Enter Name: *"Evening Task Wrapup"*, WHEN: Daily 8:00 PM, THEN: Review pending tasks.
3. Set Autonomy to `ASK` and Approval Policy to `ASK_FOR_EACH_HIGH_RISK_ACTION`.
4. Click **Create Routine** and verify routine is saved.

---

## Test Scenario 3: Pre-built Routine Templates
1. Go to **Pre-built Templates** tab.
2. Click **Activate Template** on **Morning Briefing**.
3. Verify routine is instantiated and active.

---

## Test Scenario 4: Manual Routine Execution & Execution Timeline
1. On an active routine card, click **Run Now**.
2. Verify execution status notification.
3. Switch to **Execution History** tab.
4. Verify execution entry shows started time, status (`SUCCESS`), actions attempted, tools used, and verification status.

---

## Test Scenario 5: High-Risk Permission Approval Prompt
1. Run a routine containing high-risk actions (e.g. file deletion or terminal execution).
2. Verify execution status transitions to `PENDING_APPROVAL`.
3. Verify PermissionEngine approval prompt appears in UI/Trust Center.

---

## Test Scenario 6: Routine Pause, Resume, and Deletion
1. Click **Pause** button on a routine card; verify status updates to `PAUSED`.
2. Click **Play / Resume** button; verify status updates to `ACTIVE`.
3. Click **Delete** button; verify confirmation prompt and routine removal.

---

## Test Scenario 7: Voice Trigger Command
1. Open Voice Workspace session.
2. Speak command: *"Hey Saarthi, run my morning briefing"*.
3. Verify Saarthi recognizes the command and executes the Morning Briefing routine.
