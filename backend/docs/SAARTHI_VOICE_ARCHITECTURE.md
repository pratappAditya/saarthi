# Saarthi Voice Identity & Audio Session Architecture

## Overview
Saarthi's Voice Architecture provides a native Indian English and Hindi voice identity (`saarthi_voice_hi_en`), interactive voice sessions, speech synthesis (TTS), speech transcription (STT), and barge-in speech interruption.

## Voice Profile Definition (`VoiceProfile`)
```json
{
  "id": "saarthi_voice_hi_en",
  "name": "Saarthi AI Identity Voice",
  "language": "en-IN",
  "accent": "Indian English / Hindi bilingual",
  "pitch": 1.0,
  "rate": 1.0,
  "is_cloned": false
}
```

## Barge-in Interruption Flow
```
User Spoken Input --> STT Transcription Engine
                           |
                     (Barge-in Signal)
                           |
                           v
           VoiceSessionManager.interrupt_speech()
                           |
                           v
              Halts active TTS playback
                           |
                           v
            Restores Mic Listening State
```

## Entitlements & Safety
- **Permission State**: Microphone access is explicitly requested and visible in the UI (`LISTENING`, `PROCESSING`, `SPEAKING`, `MUTED`).
- **Plan Enforcement**: Interactive voice sessions require `PERSONAL` or `POWER` plan entitlements (`voice.saarthi`).
