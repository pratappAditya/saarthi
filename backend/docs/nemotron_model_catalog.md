# Saarthi Nemotron Approved Model Catalog & Recommendation Engine

## Overview
Saarthi strictly enforces the NVIDIA Nemotron AI model family. No third-party LLMs (Llama, Mistral, OpenAI, Claude, Gemini, DeepSeek, Qwen) or arbitrary model strings are permitted.

## Approved Nemotron Models

| Model ID | Display Name | Quality Tier | Performance Tier | Min RAM | Rec RAM | Min VRAM | Rec VRAM | Size (GB) |
|---|---|---|---|---|---|---|---|---|
| `nemotron-3-nano:4b` | NVIDIA Nemotron-3 Nano 4B | High | Fast | 8 GB | 16 GB | 2 GB | 4 GB | 2.4 GB |
| `nemotron-mini:4b` | NVIDIA Nemotron Mini 4B | High | Balanced | 8 GB | 16 GB | 2 GB | 4 GB | 2.7 GB |
| `nemotron:3b` | NVIDIA Nemotron 3B Light | Standard | Ultra Fast | 6 GB | 8 GB | 0 GB | 2 GB | 1.9 GB |
| `nemotron-3-8b` | NVIDIA Nemotron-3 8B Power | Ultra | High Precision | 16 GB | 32 GB | 6 GB | 8 GB | 4.9 GB |

## Hardware Recommendation Rules
1. **High-Performance (16GB+ RAM & 6GB+ Dedicated VRAM)** -> `nemotron-3-8b`
2. **Standard Workstation (8GB-16GB RAM)** -> `nemotron-3-nano:4b` (Default)
3. **Compact Workstation (8GB RAM)** -> `nemotron-mini:4b`
4. **Low-Spec System (6GB RAM)** -> `nemotron:3b`
