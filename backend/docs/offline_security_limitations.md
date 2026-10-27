# Offline Licensing Security Limitations & Threat Analysis

## Overview

Saarthi's client-side licensing system is designed to support up to **7 days of offline usage** while protecting against local tampering, clock manipulation, and license cloning. While cryptographic signature verification and high-water mark timestamp logging provide strong security, offline software running on untrusted client hardware has inherent physical and operating system limitations.

---

## Security Guarantees & Protections

1. **Token Cryptographic Tamper-Proofing**:
   - License tokens are signed with an Ed25519 vendor private key. Any modification to `plan`, `expires_at`, `status`, or `device_fingerprint` invalidates the signature and fails closed.
2. **Device Cloning Prevention**:
   - Tokens bind to hardware characteristics (Motherboard UUID, CPU ID, MAC hash). Copying a valid token to another workstation fails device fingerprint matching.
3. **Monotonic System Clock Rollback Guard**:
   - The client logs the maximum observed UTC timestamp (`last_observed_timestamp`) in SQLite on every request. Setting the system clock back triggers `CLOCK_TAMPERED` status and locks access.
4. **Persistent Local Revocation**:
   - Once a revocation signal is received from the vendor, it is recorded in `local_revocation_cache`. Local SQLite state edits cannot bypass token verification because the token payload signature remains signed by the vendor.

---

## Known Offline Security Limitations

| Threat / Attack Vector | Limitations in Offline Context | Mitigation / Compensation |
|------------------------|--------------------------------|---------------------------|
| **OS-Level Memory Injection & Hooking** | An attacker with administrator/root privileges could attach a debugger (e.g., x64dbg/GDB) or hook Python C-extensions to override signature evaluation return values (`verify_token` -> `True`). | Requires native obfuscation/binary compilation (e.g. PyArmor/Nuitka) in production installer packaging. |
| **System Clock Forward Fast-Forwarding** | If a user advances the clock into the future and then returns to present time, the high-water mark will log the future timestamp, requiring internet re-sync to reset. | Internet sync automatically refreshes the high-water mark from authoritative NTP/vendor time. |
| **Complete System OS Freeze & VM Snapshots** | A user running Saarthi inside a virtual machine can take a snapshot of an active 7-day offline state and revert the entire OS image every 6 days. | VM snapshot detection relies on hypervisor heuristics; mandatory 7-day max offline grace ensures periodic online re-validation. |
| **Full Local Storage Wiping & System Reinstall** | If a user completely deletes `saarthi.db` and goes offline, the system defaults to `UNLICENSED` state. They cannot regain access without connecting online to re-authenticate with the vendor server. | Fails closed by default (`UNLICENSED`). |
