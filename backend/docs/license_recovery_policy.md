# License Recovery & Device Replacement Policy

## Objective

To provide legitimate Saarthi customers with a smooth recovery mechanism when hardware changes, machines are replaced, or local databases become corrupted, while maintaining strict anti-cloning and licensing enforcement.

---

## 1. Hardware Change & Device Replacement

- **Scenario**: Customer purchases a new laptop or replaces motherboard/CPU on an existing workstation.
- **Policy**:
  - Each license plan specifies a maximum active device limit (Default: 2 devices for Monthly/Yearly, 1 device for Student).
  - When the device limit is reached, activating a new machine raises `ValueError("Device limit exceeded")`.
- **Recovery Workflow**:
  1. Customer logs into the Vendor Customer Control Portal or contacts Vendor Admin Support.
  2. Customer selects the old device to deactivate.
  3. Vendor Control Plane issues a device deactivation (`DELETE FROM device_activations WHERE device_fingerprint = ...`) and logs the action in `vendor_audit_logs`.
  4. Customer activates Saarthi on the new machine using their existing license key.

---

## 2. Local Database Corruption or System Format

- **Scenario**: Workstation storage crash, OS reinstall, or `saarthi.db` corruption.
- **Policy**:
  - The client application initializes a clean SQLite database and enters `UNLICENSED` status.
- **Recovery Workflow**:
  1. User opens Saarthi and enters their license key in the settings panel.
  2. Client calls `/api/license/activate` on the vendor server.
  3. Vendor verifies active subscription and issues a fresh Ed25519 signed activation token bound to the workstation hardware fingerprint.
  4. Access is restored instantaneously.

---

## 3. Clock Rollback Lockout Recovery (`CLOCK_TAMPERED`)

- **Scenario**: User accidentally sets clock to 2030 or CMOS battery failure resets system time to 1970.
- **Policy**:
  - High-water mark guard sets status to `CLOCK_TAMPERED`.
- **Recovery Workflow**:
  1. User resets operating system clock to correct UTC time via NTP sync.
  2. Saarthi connects to vendor server (`/api/license/activate` or `/api/license/status`).
  3. Vendor signed response containing authoritative server timestamp updates `clock_tamper_log` and restores `ACTIVE` status.
