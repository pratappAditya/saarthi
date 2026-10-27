# Store Beta Nemotron Setup & Model Pull Procedure

## Overview
Detailed guide covering model acquisition, storage allocation, and download recovery for `nemotron-3-nano:4b`.

---

## Model Acquisition Specifications (Section 10)
1. **Model Name**: `nemotron-3-nano:4b`
2. **Download Command**: `ollama pull nemotron-3-nano:4b`
3. **Download Size**: ~2.3 GB
4. **Disk Requirement**: 3.5 GB free disk space
5. **Corrupted Model Recovery**: If model SHA verification fails, `/ollama/diagnostics` issues state `NEMOTRON_MODEL_CORRUPTED` and re-triggers pull.
