# Saarthi Nemotron Privacy Audit

## Data Boundary & Invariants
1. **Hardware Inspection**: System hardware details (CPU, RAM, GPU, Disk) are processed 100% locally in-memory. Zero telemetry or hardware logs sent off-device.
2. **Model Lifecycle**: Model catalog lookups and recommendations happen entirely on-device without remote tracking.
3. **AI Workloads**: All resume parsing, cover letter creation, interview prep, and career chat prompts are processed exclusively by the local Nemotron LLM via Ollama on `127.0.0.1:11434`. Zero cloud LLMs or external APIs are used.
4. **Cloud Fallbacks**: Rejection logic strictly prevents cloud API fallbacks (OpenAI, Anthropic, Google, Qwen, DeepSeek).
