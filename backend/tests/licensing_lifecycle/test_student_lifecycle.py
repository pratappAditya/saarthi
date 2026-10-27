import pytest
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def student_env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_student_complete_lifecycle_and_entitlements(student_env):
    vendor, client = student_env
    fp = get_device_fingerprint()
    
    # 1. Vendor Creates Student Customer & License
    cust = vendor.create_customer("Student Alex", "alex@university.edu")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {"license_id": lic.license_id, "plan": "STUDENT", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_s1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    # 2. Entitlements Gating Check
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == LicensePlan.STUDENT
    assert ent.optimized_for_job_applications is True
    assert ent.optimized_for_email_drafting is True
    assert ent.optimized_for_calendar is True
    assert ent.can_use_privileged_terminal is False # Gated
    
    # 3. User attempts local plan tamper in DB to MONTHLY
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET plan = 'MONTHLY'")
        conn.commit()
        
    # Signature verification evaluates vendor-signed token payload ("STUDENT"), preventing local upgrade!
    st_t, ent_t, _ = client.evaluate_license(fp)
    assert ent_t.plan == LicensePlan.STUDENT
    assert ent_t.can_use_privileged_terminal is False

def test_student_to_monthly_vendor_authorized_upgrade(student_env):
    vendor, client = student_env
    fp = get_device_fingerprint()
    
    cust = vendor.create_customer("Student Bob", "bob@college.edu")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    
    # Vendor changes entitlement to MONTHLY
    upgraded_lic = vendor.change_entitlement(lic.license_id, LicensePlan.MONTHLY)
    assert upgraded_lic.plan == LicensePlan.MONTHLY
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_up1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == LicensePlan.MONTHLY
    assert ent.can_use_privileged_terminal is True

@pytest.mark.parametrize("i", range(1, 11))
def test_student_batch_isolation(student_env, i):
    vendor, client = student_env
    cust = vendor.create_customer(f"Student {i}", f"student_{i}@test.edu")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    fp = f"fp_student_{i}"
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "STUDENT", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_s_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == LicensePlan.STUDENT
    assert ent.can_use_privileged_terminal is False
