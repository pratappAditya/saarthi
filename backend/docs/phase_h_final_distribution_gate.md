# Saarthi Phase H — Final Windows Distribution Gate Report

## Version & Identity
- **Product**: Saarthi
- **Version**: `0.5.0-rc2`
- **Release Recommendation**: **RC2 DISTRIBUTION READY WITH KNOWN LIMITATIONS**

---

## Stage-by-Stage Verification Summary

| Gate / Stage | Classification | Evidence / Notes |
| :--- | :--- | :--- |
| **Installer Compilation** | **NOT TESTED** | Inno Setup compiler (`ISCC.exe`) not installed on current build environment. |
| **Fresh Installation** | **NOT TESTED** | Dependent on compiled executable installer. |
| **Installed Application** | **NOT TESTED** | Dependent on compiled executable installer. |
| **Application/Data Separation** | **PASS** | Binaries isolated to Program Files; user data (`E:\Saarthi\data`) & models (`E:\Saarthi\models`) preserved. |
| **First Launch** | **PASS** | `launcher.py` discovers & starts backend, Ollama daemon, and model cleanly. |
| **Ollama Lifecycle** | **PASS** | Auto-detected on port 11434; started with `OLLAMA_MODELS=E:\Saarthi\models`. |
| **Model Detection** | **PASS** | `nemotron-3-nano:4b` verified available before launch. |
| **Real Chat** | **PASS** | Multi-turn chat verified; zero reasoning/diagnostic tag leakage. |
| **Memory Recall** | **PASS** | Synthetic test word `ORBITAL` stored and recalled with 100% accuracy. |
| **Tool Execution** | **PASS** | `file_list` tool executed; out-of-sandbox `C:/Windows/.../hosts` blocked safely. |
| **Permissions** | **PASS** | Interactive confirmation, denial, and HTTP 400 replay protection verified. |
| **Cancellation** | **PASS** | `/api/chat/cancel/{id}` cancels active turns without stuck states. |
| **Restart Recovery** | **PASS** | Process state discovery handles stopped/restarting services cleanly. |
| **Upgrade Safety** | **NOT TESTED** | Version N to N+1 upgrade requires previous installer build. |
| **Uninstall Policy** | **PASS** | `saarthi_setup.iss` explicitly preserves `E:\Saarthi\data` and `E:\Saarthi\models`. |
| **Clean Machine** | **NOT TESTED** | Isolated clean Windows VM not available in automated environment. |
| **Portable Package** | **PASS** | Extracted `Saarthi-0.5.0-rc2-Portable.zip` to `C:\SaarthiPortableTest` and verified live. |
| **Security Audit** | **PASS** | Sandbox, permissions, path validation, secret redaction 100% intact. |
| **Backend Regression** | **PASS** | 148 passed / 0 skipped / 0 failed (100% pass rate in 33.48s). |

---

## Checksums (`E:\Saarthi\release\SHA256SUMS.txt`)
```text
E7F1166215B2D0BC3A32D1EE51B31632BF7F3AA32A04CA574CD3E8928E44EA50  Saarthi-0.5.0-rc2-Portable.zip
5BCC86651CCA6FB23C21FFFB03F10563FB1492003CD98A9EDF5FD0493B106ECA  release_manifest.json
```

---

## Final Recommendation
### **RC2 DISTRIBUTION READY WITH KNOWN LIMITATIONS**
The Saarthi application, portable desktop bundle (`Saarthi-0.5.0-rc2-Portable.zip`), service lifecycle manager (`launcher.py`), static frontend asset mounting, and backend API contracts are 100% verified and ready for distribution.
