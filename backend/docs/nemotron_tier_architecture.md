# Saarthi Nemotron Performance Tiers Architecture

## Tiers Overview
Saarthi defines four performance tiers for local NVIDIA Nemotron model execution:

1. **STANDARD (`nemotron:3b`)**: Entry-level local model for low-spec PCs (6GB RAM min). Fast response time.
2. **PRO (`nemotron-mini:4b`)**: Instruction-tuned 4B model for high accuracy on resume tailoring and career chat (8GB RAM min).
3. **SUPER (`nemotron-3-nano:4b`)**: High-performance 4B model with extended context window and balanced reasoning (8GB RAM min, 16GB rec).
4. **ULTRA (`nemotron-3-8b`)**: Maximum-performance 8B model for deep interview simulations and complex reasoning (16GB RAM min, dedicated GPU recommended).

## Strict Invariants
- Every tier uses verified, approved NVIDIA Nemotron models.
- No third-party LLMs or cloud API fallbacks are permitted.
