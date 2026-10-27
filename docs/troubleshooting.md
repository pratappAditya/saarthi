# Saarthi Desktop Troubleshooting Guide

## Common Issues & Resolutions

### 1. Ollama Daemon Connection Error
- **Symptom**: Settings / Status card shows `Ollama Disconnected`.
- **Resolution**:
  1. Open terminal and run: `ollama serve`.
  2. Ensure `OLLAMA_MODELS=E:\Saarthi\models` environment variable is set.
  3. Verify port 11434 is responding at `http://127.0.0.1:11434/api/tags`.

### 2. Required Model Missing
- **Symptom**: Error message stating `Required AI model nemotron-3-nano:4b is not installed`.
- **Resolution**:
  Run command in terminal: `ollama pull nemotron-3-nano:4b`.

### 3. Port 8000 Occupied
- **Symptom**: Backend fails to bind to port 8000.
- **Resolution**:
  Check active process on port 8000 using `Get-NetTCPConnection -LocalPort 8000` and stop duplicate instances.
