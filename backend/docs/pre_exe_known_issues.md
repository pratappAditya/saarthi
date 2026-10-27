# Saarthi — Pre-EXE Known Non-Blocking Issues & Technical Notes

This document lists known non-blocking issues, warnings, and implementation notes prior to Windows EXE packaging.

## Active Known Issues (Non-Blocking)

1. **Starlette TestClient Deprecation Warning**:
   - *Impact*: Pytest outputs 1 mild deprecation warning regarding `starlette.testclient` using `httpx`.
   - *Severity*: Low / Warning only.
   - *Action*: Will be updated to `httpx2` in future framework updates. No runtime impact on application executable.

2. **Ollama Initial Cold Load Latency**:
   - *Impact*: If Ollama daemon is not pre-started before Saarthi launches, initial socket connection retry takes ~1.2s.
   - *Severity*: Low.
   - *Action*: Saarthi gracefully handles starting state with user-facing status indicator and retry prompt.

3. **PDF Document Text Extraction**:
   - *Impact*: Direct binary PDF text extraction falls back to plain-text resume import parsing if PyPDF2 / pdfplumber is uninstalled.
   - *Severity*: Low.
   - *Action*: Recommended to package PDF parser tools in electron/PyInstaller bundler.

## P0 / P1 Issue Status
- **Critical Security Issues**: 0
- **Hardcoded Personal Names in Production State**: 0
- **Fake Hardware Data**: 0
- **Unapproved Cloud AI Fallbacks**: 0
- **Hardcoded E:/Saarthi File Paths**: 0 (Fixed)
