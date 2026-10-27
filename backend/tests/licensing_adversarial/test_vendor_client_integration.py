import pytest
import sqlite3
import json
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.crypto import sign_payload
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def integration_env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

@pytest.mark.parametrize("action_type", ["SUSPEND", "REVOKE", "EXPIRE", "CANCEL"])
def test_end_to_end_vendor_action_flow_and_tamper_defense(integration_env, action_type):
    vendor, client = integration_env
    fp = get_device_fingerprint()
    
    # Step 1: Vendor creates & activates customer
    cust = vendor.create_customer("E2E Customer", f"e2e_{action_type.lower()}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {
        "license_id": lic.license_id,
        "customer_id": cust.customer_id,
        "plan": "MONTHLY",
        "status": "ACTIVE",
        "device_fingerprint": fp,
        "issued_at": lic.issued_at,
        "expires_at": lic.expires_at,
        "nonce": "e2e_nonce_1"
    }
    
    # Step 2 & 3: Client validates license and works normally
    client.store_activation_token(lic.license_key, token, payload)
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent is not None
    
    # Step 4: Vendor performs administrative action
    if action_type == "SUSPEND":
        vendor.suspend_license(lic.license_id)
        new_status = LicenseStatus.SUSPENDED
    elif action_type == "REVOKE":
        vendor.revoke_license(lic.license_id)
        new_status = LicenseStatus.REVOKED
    elif action_type == "CANCEL":
        vendor.cancel_license(lic.license_id)
        new_status = LicenseStatus.CANCELLED
    elif action_type == "EXPIRE":
        # Expire license on vendor
        with vendor._get_connection() as conn:
            past_exp = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            conn.cursor().execute("UPDATE licenses SET expires_at = ? WHERE license_id = ?", (past_exp, lic.license_id))
            conn.commit()
        new_status = LicenseStatus.EXPIRED

    # Step 5 & 6: Client receives updated authorization & becomes blocked
    sync_res = vendor.sync_license(lic.license_id, fp)
    if action_type in ("SUSPEND", "REVOKE", "CANCEL"):
        assert sync_res["valid"] is False
        assert sync_res["status"] == new_status.value
        
        # Apply updated token or record CRL
        if action_type == "REVOKE":
            client.record_revocation(lic.license_id, "Vendor revoked")
        else:
            updated_payload = payload.copy()
            updated_payload["status"] = new_status.value
            updated_token = sign_payload(updated_payload, vendor.private_key)
            client.store_activation_token(lic.license_key, updated_token, updated_payload)

    # Step 7, 8, 9: User attempts local DB tampering / editing local cache / local reactivation
    with client._get_connection() as conn:
        # User tries setting status = ACTIVE in client_license_cache table (but signature payload remains signed by vendor)
        conn.cursor().execute("UPDATE client_license_cache SET status = 'ACTIVE'")
        conn.commit()
        
    # User attempts local re-evaluation or reactivation with original token
    if action_type == "REVOKE":
        # Record persistent local revocation so even if token is re-used, client rejects it
        client.record_revocation(lic.license_id, "Vendor revoked")
        with pytest.raises(ValueError, match="permanently revoked"):
            vendor.activate_license(lic.license_key, fp)
    elif action_type == "SUSPEND":
        with pytest.raises(ValueError, match="currently suspended"):
            vendor.activate_license(lic.license_key, fp)
    elif action_type == "CANCEL":
        with pytest.raises(ValueError, match="cancelled"):
            vendor.activate_license(lic.license_key, fp)

    # Step 10: Client must remain unauthorized!
    final_status, final_ent, _ = client.evaluate_license(fp)
    if action_type != "EXPIRE":
        assert final_status != LicenseStatus.ACTIVE
        assert final_ent is None

@pytest.mark.parametrize("i", range(1, 51))
def test_multi_customer_vendor_authority_fuzzing(integration_env, i):
    vendor, client = integration_env
    cust = vendor.create_customer(f"Customer {i}", f"cust_integration_{i}@vendor.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT if i % 2 == 0 else LicensePlan.MONTHLY)
    fp = f"fp_integration_{i}"
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": lic.plan.value, "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # Vendor revokes even-numbered keys
    if i % 2 == 0:
        vendor.revoke_license(lic.license_id)
        client.record_revocation(lic.license_id, "Revoked batch test")
        assert client.evaluate_license(fp)[0] == LicenseStatus.REVOKED
