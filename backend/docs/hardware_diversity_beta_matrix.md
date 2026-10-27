# Saarthi — Hardware Diversity Beta Matrix Report

**Validation Date**: August 20, 2026  
**Repository**: `E:\Saarthi`  
**Evaluation Scope**: Physical Machine Hardware Diversity & Performance Classification  

---

## 1. Physical Hardware Tier Coverage Matrix

| Tier | Physical Machine Tested | Hardware Profile Specs | Recommended Nemotron Model | Measured Performance | Result |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **STANDARD** | **NO** | 6–8 GB RAM, Integrated GPU | `nemotron:3b` | `NOT PHYSICALLY TESTED` (Evaluated via software recommendation engine logic) | **`NOT PHYSICALLY AVAILABLE`** |
| **PRO** | **YES** | 16+ GB RAM, 4 GB VRAM (GTX 1650 Ti) | `nemotron-mini:4b` | 1.15s load, ~5.2 tok/s, 54MB process RAM | **`PASS`** |
| **SUPER** | **YES** | 23.8 GB RAM, 4 GB VRAM (GTX 1650 Ti) | `nemotron-3-nano:4b` | 1.18s load, 4.75 tok/s, 1,516ms latency | **`PASS WITH LIMITATIONS`** |
| **ULTRA** | **NO** | 16+ GB RAM, 6+ GB VRAM (RTX Series) | `nemotron-3-8b` | `NOT PHYSICALLY TESTED` (Requires dedicated 6GB+ VRAM GPU hardware) | **`NOT PHYSICALLY AVAILABLE`** |

---

## 2. Empirical Physical Workstation Benchmark (`OBSERVED_REAL`)

Physical host workstation measurements collected via `HardwareDetectionService` and live local Ollama inference (`nemotron-3-nano:4b`):

- **Host OS**: `Windows 11 (build 10.0.26220, AMD64)`
- **CPU**: `Intel64 Family 6 Model 165 Stepping 2, GenuineIntel` (8 Physical Cores, 24.5% idle / 46.4% load)
- **System RAM**: `23.8 GB Total` (8.1 GB Available)
- **Dedicated GPU**: `NVIDIA GeForce GTX 1650 Ti` (4.0 GB Dedicated VRAM)
- **Free SSD Storage**: `232.9 GB Free`
- **Ollama Endpoint**: `http://127.0.0.1:11434` (Online & Connected)
- **Hardware Profiling Time**: **194.64 ms**
- **Ollama Socket Ping Latency**: **26.33 ms**
- **Cold Model Load Time**: **1.18 seconds**
- **First-Token Latency (approx)**: **1,516.69 ms**
- **Generation Speed**: **4.75 tokens/sec**
- **Process Memory Footprint**: **55.5 MB RAM**
- **Sustained Memory Growth (10 cycles)**: **+12.4 MB** (No memory leaks)

---

## 3. Tier Recommendation Engine Guardrails (`DERIVED`)

The recommendation engine (`NemotronRecommendationService`) evaluated all 4 approved performance tiers against physical host specifications:

1. **`STANDARD` (`nemotron:3b`)**: `COMPATIBLE` & `RECOMMENDED` (Satisfies 6GB RAM minimum).
2. **`PRO` (`nemotron-mini:4b`)**: `COMPATIBLE` & `RECOMMENDED` (Satisfies 8GB RAM / 2GB VRAM minimum).
3. **`SUPER` (`nemotron-3-nano:4b`)**: **`RECOMMENDED TIER`** (Satisfies 8GB RAM / 2GB VRAM / 5GB storage).
4. **`ULTRA` (`nemotron-3-8b`)**: **`INSUFFICIENT_VRAM`** (`INCOMPATIBLE`, correctly rejected due to 4.0 GB VRAM < 6.0 GB VRAM required).
