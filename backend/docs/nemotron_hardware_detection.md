# Saarthi Nemotron Hardware Capability Detection Architecture

## Overview
Saarthi implements an air-gapped, zero-telemetry hardware detection service (`app.models.hardware.HardwareDetectionService`) to analyze PC capabilities for local Nemotron LLM inference.

## Specifications Collected
- **CPU**: Model identifier, physical core count, architecture (`x64`/`arm64`).
- **RAM**: Total system memory and current available memory (GB).
- **GPU**: Device name, vendor (`NVIDIA`, `AMD`, `Intel`), and total VRAM (GB). Uses `nvidia-smi` and Windows CIM/WMI.
- **Disk**: Free disk space (GB) on Saarthi workspace drive.
- **OS**: Windows build and platform version.

## Privacy Guarantee
Hardware specifications are evaluated locally strictly in-memory. Specs are never uploaded or sent to external servers or cloud services.
