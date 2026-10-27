# Saarthi — Closed Beta v1.0.0-beta.1 Release Notes

**Release Date**: August 20, 2026  
**Build Tag**: `v1.0.0-beta.1-RC1`  

---

## What's New in Saarthi Closed Beta

- **Integrated AI Studio UI/UX**: Feature-complete integration of the AI Studio modern career operating system interface.
- **Four Experience Modes**: Choose between **SIGNATURE**, **FORGE**, **PULSE**, and **AURORA** shells for personalized visual ergonomics.
- **Hardware-Aware Nemotron Tiering**: Automatic detection of CPU, RAM, GPU, VRAM, and storage to recommend the optimal NVIDIA Nemotron model (`STANDARD`, `PRO`, `SUPER`, or `ULTRA`).
- **Context Window Optimization**: `num_ctx=4096` configuration delivers a **2.88x speedup** (up to ~16.14 tokens/sec) on mid-range 4GB VRAM mobile GPUs.
- **100% Local AI Privacy**: Zero cloud LLM fallbacks. All career optimization workflows execute locally via Ollama (`http://127.0.0.1:11434`).
- **Commercial Pricing & Watermark Entitlements**: Support for Free (watermarked), Student (₹99/$1.50), Personal (₹399/$5), and Power (₹799/$10) plans.
- **Atomic Model Upgrade & Rollback**: Safe tier switching with health check verification and instant automatic rollback on failure.
