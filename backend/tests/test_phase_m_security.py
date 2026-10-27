import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.licensing.vendor_server import VendorServer
from app.licensing.models import LicensePlan, LicenseStatus

client = TestClient(app)

def test_vendor_admin_security_unauthenticated_rejection():
    # Attempt to list vendor customers without header -> Should fail 401 Unauthorized
    resp = client.get("/api/vendor/customers")
    assert resp.status_code == 401
    assert "Unauthorized" in resp.json()["detail"]

    # Attempt to create customer without header -> Should fail 401
    resp_create = client.post("/api/vendor/customers", json={"name": "Attacker", "email": "attacker@evil.com"})
    assert resp_create.status_code == 401

def test_vendor_admin_backdoor_rejection():
    # Backdoor 'dev_admin_key' must be strictly rejected (HTTP 401)
    resp = client.get("/api/vendor/customers", headers={"X-Vendor-Admin-Key": "dev_admin_key"})
    assert resp.status_code == 401
    assert "Insecure or revoked admin key rejected" in resp.json()["detail"] or "Unauthorized" in resp.json()["detail"]

    # Insecure default placeholder must also be rejected
    resp_ph = client.get("/api/vendor/customers", headers={"X-Vendor-Admin-Key": "saarthi_vendor_secret_key_change_in_production"})
    assert resp_ph.status_code == 401

    # Arbitrary incorrect key must be rejected
    resp_wrong = client.get("/api/vendor/customers", headers={"X-Vendor-Admin-Key": "wrong_key_xyz"})
    assert resp_wrong.status_code == 401

def test_vendor_admin_security_authenticated_access():
    from app.admin.auth.admin_auth import get_configured_admin_key
    valid_key = get_configured_admin_key()
    assert valid_key is not None
    headers = {"X-Vendor-Admin-Key": valid_key}
    
    # Valid list customers call
    resp = client.get("/api/vendor/customers", headers=headers)
    assert resp.status_code == 200
    assert "customers" in resp.json()

    # Valid create customer call
    resp_create = client.post("/api/vendor/customers", headers=headers, json={"name": "Alice Student", "email": "alice@university.ac.in"})
    assert resp_create.status_code == 200
    cust_id = resp_create.json()["customer"]["customer_id"]

    # Valid create license call
    resp_lic = client.post("/api/vendor/licenses", headers=headers, json={"customer_id": cust_id, "plan": "STUDENT"})
    assert resp_lic.status_code == 200
    lic_id = resp_lic.json()["license"]["license_id"]

    # Suspend license call
    resp_sus = client.post(f"/api/vendor/licenses/{lic_id}/suspend", headers=headers)
    assert resp_sus.status_code == 200

    # Restore license call
    resp_res = client.post(f"/api/vendor/licenses/{lic_id}/restore", headers=headers)
    assert resp_res.status_code == 200

def test_license_lifecycle_transitions():
    vendor = VendorServer()
    cust = vendor.create_customer("Lifecycle Test User", "lifecycle@test.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT, duration_days=30)
    
    assert lic.status == LicenseStatus.ACTIVE
    
    # Suspend
    vendor.suspend_license(lic.license_id)
    updated_sus = vendor.get_license(lic.license_id)
    assert updated_sus.status == LicenseStatus.SUSPENDED
    
    # Restore
    vendor.restore_license(lic.license_id)
    updated_res = vendor.get_license(lic.license_id)
    assert updated_res.status == LicenseStatus.ACTIVE
    
    # Renew
    renewed = vendor.renew_license(lic.license_id, extension_days=60)
    assert renewed is not None
    assert renewed.status == LicenseStatus.ACTIVE

    # Revoke
    vendor.revoke_license(lic.license_id)
    updated_rev = vendor.get_license(lic.license_id)
    assert updated_rev.status == LicenseStatus.REVOKED
