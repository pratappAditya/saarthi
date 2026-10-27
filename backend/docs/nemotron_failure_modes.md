# Saarthi Nemotron Structured Failure Modes & Diagnostics

| Diagnostic Code | Description | Recovery Action |
|---|---|---|
| `OLLAMA_NOT_INSTALLED` | Ollama daemon is missing from 127.0.0.1:11434. | Prompt user to launch Ollama setup flow. |
| `OLLAMA_OFFLINE` | Ollama service is stopped or unresponsive. | Instruct user to restart Ollama desktop app. |
| `NEMOTRON_MODEL_NOT_APPROVED` | Non-Nemotron model was requested. | Enforce selection of approved Nemotron tier. |
| `NEMOTRON_MODEL_MISMATCH` | Model string does not match catalog. | Reset active model to default Nemotron spec. |
| `INSUFFICIENT_STORAGE` | Free disk space is below required model footprint. | Prompt user to clear unused models or disk space. |
| `MODEL_HEALTH_CHECK_FAILED` | Local inference test returned error or empty text. | Automatically roll back to previously working model. |
