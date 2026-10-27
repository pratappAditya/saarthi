# Phase 5H — Advanced Voice & Hands-Free Manual QA Protocol

## Pre-requisites
1. Start Saarthi backend: `uvicorn main:app --reload`
2. Start Saarthi frontend: `npm run dev`

---

## Test Scenario 1: Voice Session Initialization & Microphone Permission
1. Click **Start Voice Session** in Voice Workspace or press `Ctrl+K` -> **Start Voice Conversation Session**.
2. Verify browser requests microphone permission (or shows active permission badge).
3. Confirm session state transitions to `LISTENING`.

---

## Test Scenario 2: True Barge-in Speech Interruption
1. Initiate a voice turn that produces long speech output.
2. While Saarthi is speaking, say "Wait, stop" or click **Barge-in Interrupt**.
3. Verify TTS audio halts immediately.
4. Confirm state transitions to `INTERRUPTED` then restores to `LISTENING`.
5. Verify current transcript and agent task graph remain uncorrupted.

---

## Test Scenario 3: Hands-Free Continuous Conversation Mode
1. Click **Enable Hands-Free**.
2. Verify persistent top banner appears with `HANDS-FREE ACTIVE`.
3. Speak turn 1 ("Explain React hooks").
4. Wait for response to finish. Verify session remains in `LISTENING` mode without needing to click start again.
5. Click **Stop Hands-Free** to exit.

---

## Test Scenario 4: Push-to-Talk Mode
1. Click or trigger **Push-to-Talk Mode**.
2. Press and hold to record turn.
3. Release button; verify state transitions to `TRANSCRIBING` -> `THINKING` -> `SPEAKING`.

---

## Test Scenario 5: Bilingual Indian English & Hindi Interaction
1. Speak or enter Hindi turn: `"Isme kya important points hain summary bana do."`
2. Confirm Saarthi responds with bilingual contextual summary while maintaining `saarthi_voice_hi_en` voice profile.

---

## Test Scenario 6: Voice + Consequential Action Approvals
1. Speak high-risk command: `"Tailor my resume and apply for this position."`
2. Verify Saarthi transitions to `WAITING_FOR_APPROVAL` state.
3. Verify explicit Approval Card appears on screen detailing action risk level and description.
4. Click **Approve & Execute** to resume.

---

## Test Scenario 7: Trust Center Voice Privacy Verification
1. Navigate to **Trust Center** (`/trust`).
2. Verify **VOICE PRIVACY CENTER** section displays:
   - Microphone Access: Explicit Consent Required
   - STT/TTS Processing: Local Saarthi Engine (100% Local)
   - Wake-Word Policy: WakeWordProvider Boundary Active
