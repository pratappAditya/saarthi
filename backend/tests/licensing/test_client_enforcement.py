import pytest
import sqlite3
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan, Entitlements
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.middleware import verify_active_license, require_entitlement
from app.licensing.device import get_device_fingerprint
from fastapi import HTTPException

@pytest.fixture
def vendor_and_client():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_client_unlicensed_by_default(vendor_and_client):
    _, client = vendor_and_client
    status, entitlements, msg = client.evaluate_license()
    assert status == LicenseStatus.UNLICENSED
    assert entitlements is None

def test_client_active_license_flow(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("User 1", "u1@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    fp = "fp_client_machine_100"
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {
        "license_id": lic.license_id,
        "plan": "MONTHLY",
        "status": "ACTIVE",
        "device_fingerprint": fp,
        "issued_at": lic.issued_at,
        "expires_at": lic.expires_at
    }
    client.store_activation_token(lic.license_key, token, payload)
    
    status, entitlements, msg = client.evaluate_license(fp)
    assert status == LicenseStatus.ACTIVE
    assert entitlements is not None
    assert entitlements.plan == LicensePlan.MONTHLY
    assert entitlements.can_use_privileged_terminal is True

@pytest.mark.parametrize("plan,expected_job_opt,expected_term", [
    (LicensePlan.MONTHLY, True, True),
    (LicensePlan.YEARLY, True, True),
    (LicensePlan.STUDENT, True, False),
])
def test_client_plan_entitlements_gating(vendor_and_client, plan, expected_job_opt, expected_term):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("User Plan", f"u_{plan.value}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=plan)
    
    fp = "fp_client_machine_plan"
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {
        "license_id": lic.license_id,
        "plan": plan.value,
        "status": "ACTIVE",
        "device_fingerprint": fp,
        "issued_at": lic.issued_at,
        "expires_at": lic.expires_at
    }
    client.store_activation_token(lic.license_key, token, payload)
    
    status, entitlements, _ = client.evaluate_license(fp)
    assert status == LicenseStatus.ACTIVE
    assert entitlements.optimized_for_job_applications == expected_job_opt
    assert entitlements.can_use_privileged_terminal == expected_term

def test_client_expired_license_evaluation(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("Expired User", "exp@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=-1)
    
    # Attempting to activate expired key on vendor raises ValueError
    with pytest.raises(ValueError, match="expired"):
        vendor.activate_license(lic.license_key, "fp_1")

def test_middleware_verify_active_license_success(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("Mid User", "mid@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = get_device_fingerprint()
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    ent = verify_active_license(client_manager=client)
    assert ent.plan == LicensePlan.MONTHLY

def test_middleware_verify_active_license_unlicensed_raises_403(vendor_and_client):
    _, client = vendor_and_client
    with pytest.raises(HTTPException) as exc_info:
        verify_active_license(client_manager=client)
    assert exc_info.value.status_code == 403

def test_middleware_require_entitlement_gating(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("Student User", "student_gate@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    fp = get_device_fingerprint()
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"plan": "STUDENT", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    ent = verify_active_license(client_manager=client)
    
    checker_term = require_entitlement("can_use_privileged_terminal")
    with pytest.raises(HTTPException) as exc_info:
        checker_term(entitlements=ent)
    assert exc_info.value.status_code == 403
    
    checker_job = require_entitlement("optimized_for_job_applications")
    res = checker_job(entitlements=ent)
    assert res.plan == LicensePlan.STUDENT

@pytest.mark.parametrize("idx,plan_type", [(i, LicensePlan.STUDENT if i % 3 == 0 else (LicensePlan.YEARLY if i % 3 == 1 else LicensePlan.MONTHLY)) for i in range(1, 31)])
def test_client_entitlements_matrix(vendor_and_client, idx, plan_type):
    vendor, client = vendor_and_client
    cust = vendor.create_customer(f"User {idx}", f"user_matrix_{idx}@test.org")
    lic = vendor.create_license(cust.customer_id, plan=plan_type)
    fp = f"fp_matrix_device_{idx}"
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"plan": plan_type.value, "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == plan_type
