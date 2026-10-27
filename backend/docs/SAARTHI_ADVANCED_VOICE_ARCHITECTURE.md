# Saarthi Advanced Voice & Hands-Free Architecture

## 1. System Architecture

```
User Voice Input / Push-to-Talk / Hands-Free Loop
                     │
                     ▼
         ┌────────────────────────┐
         │ VoiceConversationEngine│ (Deterministic State Machine)
         └───────────┬────────────┘
                     │
         ┌───────────┴────────────┐
         │  STTProvider (Local)   │ ──► Indian English & Hindi Transcripts
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │ Intelligence Core      │ ──► Memory, DomainRouter, Multimodal, AgentRuntime
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │ PermissionEngine       │ ──► Human-in-the-loop Approval if High Risk
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  TTSProvider (Local)   │ ──► saarthi_voice_hi_en Speech Output
         └───────────┬────────────┘
                     │
                     ▼
              True Barge-In
         (Halts TTS & Restores Mic)
```

## 2. Voice State Machine States
- `IDLE`: Engine ready for turn initiation.
- `REQUESTING_MIC_PERMISSION`: Microphone permission request active.
- `LISTENING`: Audio stream active or listening for hands-free turn.
- `TRANSCRIBING`: Speech-to-text processing.
- `THINKING`: Context resolution, domain routing, reasoning, and tool planning.
- `WAITING_FOR_APPROVAL`: Consequential action requires user confirmation.
- `EXECUTING`: Agent or tool execution in progress.
- `SPEAKING`: Text-to-speech audio synthesis & output playback.
- `INTERRUPTED`: Barge-in signal received; TTS halted immediately.
- `CANCELLED`: Session or turn explicitly cancelled by user.
- `ERROR`: Recoverable error state with deterministic cleanup.

## 3. Provider Abstractions
- `STTProvider`: Audio chunk transcription, streaming support, language hint handling.
- `TTSProvider`: Speech synthesis for `saarthi_voice_hi_en` persona with rate/pitch control.
- `WakeWordProvider`: Boundary for "Hey Saarthi" wake word with explicit user permission.
- `VoiceActivityDetector`: VAD & silence duration detection.

## 4. Privacy & Entitlement Rules
- **No Background Recording**: Microphone active only when session is explicitly started.
- **Local First**: Zero raw audio transferred to external servers.
- **Entitlement Mapping**:
  - `voice.input` & `voice.output`: Student+
  - `voice.realtime`, `voice.saarthi`, `voice.wake_word`: Personal+
  - `voice.proactive`: Power+
