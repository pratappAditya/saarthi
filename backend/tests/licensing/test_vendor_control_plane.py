import pytest
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer
from app.licensing.crypto import verify_token

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_vendor_create_customer_success(vendor):
    cust = vendor.create_customer("Alice Developer", "alice@example.com")
    assert cust.customer_id.startswith("CUST-")
    assert cust.name == "Alice Developer"
    assert cust.email == "alice@example.com"

def test_vendor_create_customer_duplicate_email(vendor):
    vendor.create_customer("Alice", "alice@example.com")
    with pytest.raises(ValueError, match="already exists"):
        vendor.create_customer("Alice Duplicate", "alice@example.com")

def test_vendor_list_and_get_customer(vendor):
    c1 = vendor.create_customer("Bob", "bob@example.com")
    c2 = vendor.create_customer("Charlie", "charlie@example.com")
    
    customers = vendor.list_customers()
    assert len(customers) == 2
    assert vendor.get_customer(c1.customer_id).name == "Bob"

@pytest.mark.parametrize("plan", [LicensePlan.MONTHLY, LicensePlan.YEARLY, LicensePlan.STUDENT])
def test_vendor_create_license_plans(vendor, plan):
    cust = vendor.create_customer("Dev", f"dev_{plan.value}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=plan)
    assert lic.plan == plan
    assert lic.status == LicenseStatus.ACTIVE
    assert lic.license_key.startswith(f"SAARTHI-{plan.value[:3]}-")

def test_vendor_activate_license_success(vendor):
    cust = vendor.create_customer("Dev", "dev@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    token = vendor.activate_license(lic.license_key, "fp_device_1", "Workstation 1")
    assert token is not None
    payload = verify_token(token, vendor.public_key)
    assert payload["license_id"] == lic.license_id
    assert payload["device_fingerprint"] == "fp_device_1"
    assert payload["plan"] == "MONTHLY"

def test_vendor_activate_device_limit_exceeded(vendor):
    cust = vendor.create_customer("Dev", "dev_limit@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=2)
    
    vendor.activate_license(lic.license_key, "fp_dev_1")
    vendor.activate_license(lic.license_key, "fp_dev_2")
    
    with pytest.raises(ValueError, match="Device limit exceeded"):
        vendor.activate_license(lic.license_key, "fp_dev_3")

def test_vendor_re_activate_same_device(vendor):
    cust = vendor.create_customer("Dev", "dev_same@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=1)
    
    t1 = vendor.activate_license(lic.license_key, "fp_dev_1")
    t2 = vendor.activate_license(lic.license_key, "fp_dev_1")
    assert t1 != t2 # Different nonces

def test_vendor_suspend_and_restore_license(vendor):
    cust = vendor.create_customer("Dev", "dev_susp@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    assert vendor.suspend_license(lic.license_id, reason="Payment failed") is True
    with pytest.raises(ValueError, match="currently suspended"):
        vendor.activate_license(lic.license_key, "fp_1")
        
    assert vendor.restore_license(lic.license_id) is True
    token = vendor.activate_license(lic.license_key, "fp_1")
    assert token is not None

def test_vendor_revoke_license_permanent(vendor):
    cust = vendor.create_customer("Dev", "dev_rev@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    assert vendor.revoke_license(lic.license_id, reason="Breach of Terms") is True
    with pytest.raises(ValueError, match="permanently revoked"):
        vendor.activate_license(lic.license_key, "fp_1")
        
    # Cannot restore revoked license
    assert vendor.restore_license(lic.license_id) is False

def test_vendor_renew_license(vendor):
    cust = vendor.create_customer("Dev", "dev_renew@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=30)
    
    renewed = vendor.renew_license(lic.license_id, extension_days=60)
    assert renewed is not None
    assert renewed.status == LicenseStatus.ACTIVE

def test_vendor_change_entitlement(vendor):
    cust = vendor.create_customer("Student Dev", "student@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    
    updated = vendor.change_entitlement(lic.license_id, LicensePlan.YEARLY)
    assert updated.plan == LicensePlan.YEARLY

def test_vendor_audit_log_tracking(vendor):
    cust = vendor.create_customer("Audit User", "audit@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    vendor.suspend_license(lic.license_id)
    
    logs = vendor.get_audit_logs(lic.license_id)
    actions = [l.action for l in logs]
    assert "CREATE_LICENSE" in actions
    assert "SUSPEND_LICENSE" in actions

def test_vendor_get_crl(vendor):
    c = vendor.create_customer("CRL User", "crl@example.com")
    l1 = vendor.create_license(c.customer_id, plan=LicensePlan.MONTHLY)
    l2 = vendor.create_license(c.customer_id, plan=LicensePlan.YEARLY)
    
    vendor.revoke_license(l1.license_id)
    vendor.suspend_license(l2.license_id)
    
    crl = vendor.get_crl()
    rev_ids = [item["license_id"] for item in crl]
    assert l1.license_id in rev_ids
    assert l2.license_id in rev_ids

@pytest.mark.parametrize("i", range(1, 31))
def test_vendor_fuzz_customer_and_license_creation(vendor, i):
    cust = vendor.create_customer(f"Customer {i}", f"cust_{i}@test.org")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT if i % 2 == 0 else LicensePlan.MONTHLY)
    assert lic.customer_id == cust.customer_id
    token = vendor.activate_license(lic.license_key, f"fp_device_{i}")
    assert token is not None
