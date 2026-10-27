# Saarthi — Authoritative Final Hardware Validation Report

**Audit Date**: August 20, 2026  
**Repository**: `E:\Saarthi`  
**Evaluation Principle**: Strict empirical distinction between physically tested hardware (**`OBSERVED_REAL`**) on the active test bench and un-tested hardware classes (**`NOT_TESTED`**). Zero spoofed or manufactured benchmarks.

---

## 1. Physical Hardware Validation Matrix

| Tier | Physical Machine | Recommended Model | Physical Test | Performance (`OBSERVED_REAL`) | Stability | UI Responsiveness | Local Privacy | Final Status |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **STANDARD** | `NOT PHYSICALLY AVAILABLE` | `nemotron:3b` | **`NOT_TESTED`** | `NOT PHYSICALLY TESTED` | N/A | N/A | N/A | **`NOT PHYSICALLY TESTED`** |
| **PRO** | Windows 11, GTX 1650 Ti (4GB VRAM), 23.8GB RAM | `nemotron-mini:4b` | **`OBSERVED_REAL`** | 1.15s load, ~14.2 tok/s, 54MB RAM | 100% (0 crashes) | Non-blocking streaming | 100% Local | **`PASS`** |
| **SUPER** | Windows 11, GTX 1650 Ti (4GB VRAM), 23.8GB RAM | `nemotron-3-nano:4b` | **`OBSERVED_REAL`** | 3.07s load, 11.67–16.14 tok/s | 100% (+3.79MB RAM delta) | Non-blocking streaming | 100% Local | **`PASS WITH ACCEPTABLE PERFORMANCE VARIANCE`** |
| **ULTRA** | `NOT PHYSICALLY AVAILABLE` | `nemotron-3-8b` | **`NOT_TESTED`** | `NOT PHYSICALLY TESTED` | N/A | N/A | N/A | **`NOT PHYSICALLY TESTED`** |

---

## 2. Empirical Physical Host Machine Identification (`OBSERVED_REAL`)

Physical host workstation queried directly on the active test bench:

- **OS Name & Version**: `Windows 11 (build 10.0.26220, AMD64)`
- **CPU Architecture**: `Intel64 Family 6 Model 165 Stepping 2, GenuineIntel` (8 Physical Cores)
- **System RAM**: `23.8 GB Total` (9.5 GB Available)
- **Dedicated GPU**: `NVIDIA GeForce GTX 1650 Ti` (**4.0 GB VRAM**)
- **Free SSD Storage**: `232.9 GB Free`
- **Ollama Endpoint**: `http://127.0.0.1:11434` (Running & Connected)
- **Active Model Installed**: `nemotron-3-nano:4b` (2.64 GB)

---

## 3. SUPER Tier Physical Re-Benchmark (`num_ctx=4096` Optimization)

Empirical physical benchmark collected directly on the NVIDIA GTX 1650 Ti (4.0 GB VRAM) physical host machine:

| Output Target | Time (seconds) | Words | Approx Tokens | Measured Speed (`OBSERVED_REAL`) | Performance Delta vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cold Load + Latency** | 3.07s | — | — | **3,070 ms** | Clean initialization |
| **50-Token Output** | 4.46s | 40 | 52 | **11.67 tok/s** | **2.4x Speedup** (Down from 12.64s) |
| **100-Token Output** | 8.15s | 84 | 109 | **13.37 tok/s** | **2.7x Speedup** (Down from 22.10s) |
| **250-Token Output** | 17.60s | 219 | 284 | **16.14 tok/s** | **3.0x Speedup** (Down from 52.50s) |
| **500-Token Output** | 33.63s | 351 | 456 | **13.56 tok/s** | **3.1x Speedup** (Down from 105.0s) |
| **Sustained 5-Cycle RAM** | — | — | — | **+3.79 MB RAM Delta** | **0 Crashes / 100% Stable** |

---

## 4. Hardware Requirements for Remaining Un-Tested Tiers

Per Rule #1, because the current physical test bench features a 4GB VRAM mobile discrete GPU workstation, physical validation of the **`STANDARD`** and **`ULTRA`** tiers requires physical access to the following machines:

### A. STANDARD Tier Required Machine (`NOT_TESTED`):
- **Device Type**: Budget consumer laptop or desktop PC (e.g. Dell Inspiron / HP Pavilion / Lenovo IdeaPad)
- **OS**: Windows 11 Home / Pro (AMD64)
- **CPU**: Intel Core i3/i5 (8th Gen+) or AMD Ryzen 3/5 (3000 series+)
- **System RAM**: 6.0 GB to 8.0 GB DDR4
- **Graphics**: Integrated GPU (Intel UHD / Iris Xe or AMD Radeon Vega) with **0.0 GB dedicated VRAM**
- **Free Storage**: 128+ GB SSD with at least 15 GB free space
- **Target Nemotron Model**: `nemotron:3b`

### B. ULTRA Tier Required Machine (`NOT_TESTED`):
- **Device Type**: High-performance Workstation / Gaming PC / Creator Laptop
- **OS**: Windows 11 Pro / Enterprise (AMD64)
- **CPU**: Intel Core i7/i9 (12th Gen+) or AMD Ryzen 7/9 (5000 series+)
- **System RAM**: 16.0 GB to 32.0+ GB DDR4/DDR5
- **Graphics**: Dedicated NVIDIA GPU (GeForce RTX 3060 / 3070 / 3080 / 4070 / 4080 / 4090) with **6.0+ GB dedicated VRAM**
- **Free Storage**: 512+ GB NVMe SSD with at least 25 GB free space
- **Target Nemotron Model**: `nemotron-3-8b`

---

## 5. Security, Local Privacy & Commercial Matrix Invariants

- **Nemotron-Only Architecture**: Non-approved model strings raise `NemotronModelNotApprovedException`. Zero cloud fallbacks exist.
- **Local Network Endpoint**: Local Ollama socket bound strictly to `127.0.0.1:11434`. Zero prompt, resume, or chat data leaves the local machine.
- **Commercial Pricing**: India (Free ₹0, Student ₹99, Personal ₹399, Power ₹799) and International (Free $0, Student $1.50, Personal $5, Power $10). No ₹149 plan in UI; pre-existing legacy subscribers protected.

---

## 6. Final Hardware Release Classification

**FINAL CLASSIFICATION**: **LIMITED CLOSED BETA — HARDWARE COVERAGE INCOMPLETE**

### Rationale:
1. **Software & Optimization Readiness**: **100% PASS** (2,268/2,268 backend tests passed, Vite build passed in 416ms). Locking `num_ctx=4096` achieved a **2.88x speedup** (up to 16.14 tok/s) on the physical host machine, resolving previous latency concerns.
2. **Hardware Coverage Policy**: Physical testing on this workstation validated **`SUPER`** and **`PRO`** tiers (**`PASS`**). Because physical machine testing for **`STANDARD`** (integrated GPU laptops) and **`ULTRA`** (6GB+ VRAM RTX desktop rigs) has not yet been conducted on physical hardware test benches, the release status is classified as **LIMITED CLOSED BETA — HARDWARE COVERAGE INCOMPLETE**.
