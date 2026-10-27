import pytest
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_vendor_api_invalid_customer_id_rejection(vendor):
    with pytest.raises(ValueError, match="does not exist"):
        vendor.create_license("NON_EXISTENT_CUST", plan=LicensePlan.MONTHLY)

def test_vendor_api_invalid_license_key_activation_rejection(vendor):
    with pytest.raises(ValueError, match="Invalid license key"):
        vendor.activate_license("SAARTHI-INVALID-KEY-12345", "fp_1")

def test_vendor_api_nonexistent_license_operations(vendor):
    assert vendor.suspend_license("NON_EXISTENT_LIC") is False
    assert vendor.revoke_license("NON_EXISTENT_LIC") is False
    assert vendor.restore_license("NON_EXISTENT_LIC") is False
    assert vendor.renew_license("NON_EXISTENT_LIC") is None
    assert vendor.change_entitlement("NON_EXISTENT_LIC", LicensePlan.YEARLY) is None

@pytest.mark.parametrize("i", range(1, 46))
def test_vendor_api_audit_log_completeness(vendor, i):
    cust = vendor.create_customer(f"Audit User {i}", f"audit_{i}@vendor.org", actor=f"admin_{i}")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, actor=f"admin_{i}")
    vendor.suspend_license(lic.license_id, actor=f"admin_{i}")
    
    logs = vendor.get_audit_logs(lic.license_id)
    assert len(logs) >= 2
    actors = [l.actor for l in logs]
    assert f"admin_{i}" in actors
