# Saarthi Product Demonstration — MeitY GENESIS EIR Cohort-3 Submission

This repository contains the product demonstration video `Saarthi_GENESIS_Product_Demo.mp4` generated directly from the live, un-modified working build of **Saarthi v0.5** for submission to the **MeitY GENESIS EIR Cohort-3 Evaluation Committee**.

---

## Technical Specifications of the Video
- **Filename:** `Saarthi_GENESIS_Product_Demo.mp4`
- **Location:** `E:\Saarthi\Saarthi_GENESIS_Product_Demo.mp4`
- **Resolution:** 1920×1080 (16:9 Landscape)
- **Duration:** 101.9 seconds (Target: 90–120 seconds)
- **Format:** H.264 MP4 (Video Only, No Audio Track)
- **Visual Captions:** Clean technical lower-third captions detailing each segment

---

## Features Demonstrated (Live & Unmodified Implementation)

The demonstration records the actual running web workspace (`http://localhost:5173/`) connected to the FastAPI operational backend (`http://127.0.0.1:8000/`) and demonstrates the following functional core capabilities:

1. **0:00–0:12 | Introduction & AI Studio Workbench**
   - Live opening of the Saarthi executive workbench interface (`Signature Shell`, dark graphite theme, status indicators).
   - Display of the title overlay: `SAARTHI — AI Assistant for Workflows`.

2. **0:12–0:32 | Basic Natural Language AI Interaction**
   - Real-time prompt submission via the assistant interface: `"Hello Saarthi, show your system status and capabilities."`
   - Local intent parsing, system profile retrieval, and assistant response formatting.

3. **0:32–1:05 | Strongest Working Capability: Stateful Agent Loop & Smart Tool Routing**
   - User request: `"List all the files in my project workspace folder."`
   - Smart keyword tool routing identifies relevant tools (`file_list`, `file_read`, `file_search`).
   - Execution of the sandboxed `file_list` tool on `E:\Saarthi`.
   - Complete execution lifecycle: user query → intent parsing → tool dispatch → file system scan → formatted result return.

4. **1:05–1:30 | Second Capability: Persistent SQLite Memory Subsystem**
   - User request: `"Remember my preference: I prefer dark theme for all workflow interfaces."`
   - Invocation of `suggest_memory` tool to persist user preferences in the SQLite database under category `USER`.
   - Inspection of the **Persistent Memory View** showing categorized stored facts and context scoring.

5. **1:30–1:45 | Technical / Product View: Hardware Engine & Benchmarking**
   - Demonstration of the **Nemotron Models & Hardware Panel**.
   - Inspection of system specs (CPU cores, System RAM, VRAM, free storage).
   - Real-time hardware performance metrics (`measured_tps` in tokens/sec) and diagnostics telemetry (`agent_diagnostics.log`).
   - Zero credential / key exposure guarantee.

6. **1:45–1:55 | Conclusion & TRL 3 Validation Summary**
   - Closing overlay stating current technology readiness:
     ```
     Current Stage
     TRL 3 — Proof of Concept Validation

     Saarthi
     AI Assistant for Workflows
     ```

---

## Authenticity Statement
- **Zero Mockups / Fake UIs:** Every screen and response shown in `Saarthi_GENESIS_Product_Demo.mp4` was rendered live by the Saarthi v0.5 application stack.
- **No Fabricated Revenue or Enterprise Claims:** The video strictly presents the software at its true current proof-of-concept stage.

---

## Current Operational Boundaries & Limitations (TRL 3)
1. **Workspace Sandboxing:** Tools (`file_list`, `file_read`, `file_search`) are strictly restricted to configured trusted root directories (`E:\Saarthi` and configured descendants).
2. **Local Model Hardware Dependency:** Optimal local inference speed relies on available GPU VRAM (NVIDIA / Metal) or multi-core host RAM. In offline/CPU-only mode, response latency scales with model quantization.
3. **Human-in-the-Loop Approval:** Destructive or privileged system actions require interactive user permission confirmation before execution.
