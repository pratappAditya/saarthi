# Saarthi — Real Hardware Detection & Model Pipeline Report

This document reports the physical host machine hardware detected during the Pre-EXE Production Readiness audit.

## Physical Machine Hardware Profile (Observed Real)

- **OS Name & Version**: Windows 11 (10.0.26220)
- **Architecture**: AMD64 (x86_64)
- **CPU Model**: Intel64 Family 6 Model 165 Stepping 2, GenuineIntel
- **Physical/Logical Cores**: 8
- **Total System RAM**: 23.8 GB
- **Available RAM**: 6.2 GB
- **GPU Vendor**: NVIDIA
- **GPU Model**: NVIDIA GeForce GTX 1650 Ti
- **Dedicated VRAM**: 4.0 GB GDDR6
- **Available Storage**: 232.8 GB Free SSD
- **Ollama Status**: Installed & Running (Local Socket 127.0.0.1:11434)
- **Installed Nemotron Models**: `nemotron-3-nano:4b`

## Hardware Pipeline Determination

```
Hardware Detection (NVIDIA GTX 1650 Ti 4.0GB VRAM / 23.8GB RAM)
        ↓
Tier Recommendation Engine (SUPER Tier Selected)
        ↓
Model Matching (NVIDIA Nemotron-3 Nano 4B)
        ↓
ULTRA Eligibility Gate (Ineligible for 8B Model due to <6.0GB VRAM)
        ↓
Performance Diagnostics (Active GPU Acceleration Verified)
```

## Gate Enforcement
- **ULTRA Tier (8B Model)**: Correctly blocked on 4.0GB VRAM GPUs (Requires 6.0GB+ VRAM).
- **SUPER Tier (4B Model)**: Selected and verified compatible with 4.0GB VRAM.
