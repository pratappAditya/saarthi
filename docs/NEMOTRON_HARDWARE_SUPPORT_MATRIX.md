# NVIDIA NEMOTRON HARDWARE SUPPORT MATRIX & RUNTIME SPECIFICATION
**Product:** Saarthi AI Companion  
**Publisher:** Trovane Technologies  
**Target:** Windows 10 & 11 Desktop (x64)  
**Date:** October 2026  
**Status:** Canonical Hardware Specification & Model Registry

---

## 1. Architectural Principles

1. **Hardware-Aware Adaptive Provisioning:** Saarthi inspects system CPU, available RAM, GPU vendor, dedicated VRAM, and storage before recommending or downloading any model weights.
2. **Zero Silently Substituted Models:** Saarthi never pretends local AI is operating if no local model is loaded. It never silently routes prompts to external cloud APIs without explicit user consent.
3. **No Terminal Required:** End customers do not need to open PowerShell, cmd, or run `ollama pull` manually. Download, progress tracking, cancellation, integrity validation, and smoke testing are integrated directly into the Saarthi desktop UI.
4. **Weights Segregated from Base Package:** Base Windows Store MSIX package contains only the application runtime (~122 MB). Large model weights are downloaded directly into `%USERPROFILE%\.ollama\models` or `%LOCALAPPDATA%\Saarthi\models` upon explicit consent.

---

## 2. Approved Model Registry & Specifications

| Attribute | STANDARD Tier | PRO Tier | SUPER Tier (Active Default) | ULTRA Tier |
|---|---|---|---|---|
| **Model Identifier** | `nemotron:3b` | `nemotron-mini:4b` | `nemotron-3.5-bolt-e4b` / `nemotron-3-nano:4b` | `nemotron:8b` / `nemotron-3-8b` |
| **Display Name** | NVIDIA Nemotron 3B Light | NVIDIA Nemotron Mini 4B | NVIDIA Nemotron 3.5 Bolt E4B | NVIDIA Nemotron 8B Ultra |
| **Quantization** | Q4_K_M (GGUF) | Q4_K_M (High Precision) | Q4_K_M (Lossless Calibrated) | Q5_K_M (High Fidelity) |
| **Download Size** | ~1.9 GB | ~2.7 GB | ~3.1 GB | ~4.9 GB |
| **Min / Rec System RAM** | 6.0 GB / 8.0 GB | 8.0 GB / 16.0 GB | 12.0 GB / 16.0 GB | 16.0 GB / 32.0 GB |
| **Min / Rec Dedicated VRAM**| 0.0 GB (CPU) / 2.0 GB | 2.0 GB / 4.0 GB | 3.0 GB / 6.0 GB | 6.0 GB / 8.0 GB+ |
| **Free Storage Required** | 4.0 GB | 6.0 GB | 8.0 GB | 12.0 GB |
| **Context Window Length** | 4,096 tokens | 4,096 tokens | 8,192 tokens | 8,192 tokens |
| **Estimated Overhead** | 0.8 GB RAM + 0.3 GB KV | 1.0 GB RAM + 0.5 GB KV | 1.5 GB RAM + 0.8 GB KV | 2.5 GB RAM + 1.2 GB KV |
| **Execution Device** | CPU Fallback or Entry GPU | CUDA GPU or Multi-core CPU | NVIDIA CUDA GPU (Recommended) | NVIDIA RTX Dedicated GPU |
| **Measured Throughput** | ~18 tokens/sec | ~14.2 tokens/sec | ~24.0 tokens/sec (Speculative) | Requires 6GB+ VRAM RTX |
| **License Type** | NVIDIA Open Model License | NVIDIA Open Model License | NVIDIA Open Model License | NVIDIA Open Model License |
| **Attribution Notice** | Developed by NVIDIA Corp | Developed by NVIDIA Corp | Developed by NVIDIA Corp | Developed by NVIDIA Corp |

---

## 3. Hardware Classification Policy

The recommendation engine (`app.models.recommendation.NemotronRecommendationService`) evaluates the system's `HardwareProfile` against deterministic criteria:

```
IF Total RAM < 6 GB OR Free Storage < 4 GB:
    STATUS = INSUFFICIENT_HARDWARE
    GUIDANCE = "System does not satisfy minimum hardware requirements for local Nemotron inference."

ELSE IF Dedicated VRAM >= 6.0 GB AND Total RAM >= 16.0 GB AND Free Storage >= 12.0 GB:
    RECOMMENDED_TIER = ULTRA
    MODEL = "nemotron:8b"

ELSE IF Dedicated VRAM >= 3.0 GB AND Total RAM >= 12.0 GB AND Free Storage >= 8.0 GB:
    RECOMMENDED_TIER = SUPER
    MODEL = "nemotron-3.5-bolt-e4b"

ELSE IF (Dedicated VRAM >= 2.0 GB OR Available RAM >= 8.0 GB) AND Free Storage >= 6.0 GB:
    RECOMMENDED_TIER = PRO
    MODEL = "nemotron-mini:4b"

ELSE:
    RECOMMENDED_TIER = STANDARD
    MODEL = "nemotron:3b" (CPU Execution Mode)
```

---

## 4. Storage Reclamation & Model Lifecycle

- **Download Preflight Check:** Before initiating a model pull, Saarthi validates that `free_storage_gb >= model.minimum_storage_gb + 1.0` (1 GB safety margin).
- **Download Cancellation:** Users can click "Cancel Download" at any time. The background stream is immediately aborted and partial temporary chunks are purged.
- **Model Deletion / Storage Reclamation:** Users can delete model weights via the Settings screen or API (`DELETE /api/nemotron/models/{model_id}`). Ollama runtime deletes the manifest and blob layers, instantly reclaiming 2–5 GB of disk space.
- **Real Inference Smoke Testing:** Upon download completion, Saarthi invokes `POST /api/nemotron/smoke-test` to generate a real response, measuring Time To First Token (TTFT), tokens/sec, and confirming CUDA acceleration.
