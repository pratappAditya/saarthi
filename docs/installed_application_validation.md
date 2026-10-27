# Saarthi Installed Application & Portable Package Validation

## Overview
This document records runtime validation results for the standalone portable release package (`Saarthi-0.5.0-rc2-Portable.zip`).

---

## 1. Portable Extraction Test
- **Source Archive**: `E:\Saarthi\release\Saarthi-0.5.0-rc2-Portable.zip`
- **Target Extraction Path**: `C:\SaarthiPortableTest`
- **Execution Test**: Executed `launcher.py` inside `C:\SaarthiPortableTest`.
- **Result**: **PASS**. Services discovered and verified online (`ollama_online: true`, `backend_online: true`, `model_available: true`).

---

## 2. Installed Application Test Status
- **Installed Build Execution**: **NOT TESTED** (Inno Setup compiler not present on build environment).
