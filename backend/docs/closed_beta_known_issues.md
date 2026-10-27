# Saarthi — Closed Beta Known Issues & Operational Notes

**Version**: `v1.0.0-beta.1`  
**Classification**: Closed Beta Release Candidate  

---

## Hardware-Dependent Performance Characteristics

1. **Generation Speed Variance on 4GB VRAM Hardware**:
   - On mid-range mobile GPUs (e.g. GTX 1650 Ti with 4.0 GB VRAM running `nemotron-3-nano:4b`), long-form generation (250-word cover letters or STAR interview responses) takes ~15–35 seconds (speeding up to ~13.7–16.14 tokens/sec).
   - **Workaround**: The React drawer UI streams text progress asynchronously without freezing the user interface.
2. **Integrated GPU Initial Load Latency**:
   - On integrated graphics laptops (`STANDARD` tier), initial model load time may take 5–10 seconds when starting the application.
3. **Model Upgrade Storage Requirement**:
   - Upgrading from `SUPER` (`nemotron-3-nano:4b`, ~2.6GB) to `ULTRA` (`nemotron-3-8b`, ~4.9GB) requires at least 10.0 GB free SSD storage during download and verification.

---

## Known Operational Behaviors

- **Free-Tier Watermarking**: Free tier document exports intentionally append a subtle watermark footer. Upgrading to Student (₹99/$1.50), Personal (₹399/$5), or Power (₹799/$10) enables clean unwatermarked exports instantly without re-running AI inference.
- **Offline Network Isolation**: Disconnecting the network will not disrupt AI features, as all prompt execution binds strictly to `http://127.0.0.1:11434`.
