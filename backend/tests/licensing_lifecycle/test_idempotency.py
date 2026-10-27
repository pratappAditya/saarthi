import pytest
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_idempotence_of_vendor_operations(vendor):
    cust = vendor.create_customer("Idem User", "idem@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = "fp_idem_1"
    
    # 1. Activate Twice
    t1 = vendor.activate_license(lic.license_key, fp)
    t2 = vendor.activate_license(lic.license_key, fp)
    assert t1 is not None
    assert t2 is not None
    
    # 2. Suspend Twice
    assert vendor.suspend_license(lic.license_id) is True
    assert vendor.suspend_license(lic.license_id) is True
    assert vendor.get_license(lic.license_id).status == LicenseStatus.SUSPENDED
    
    # 3. Restore Twice
    assert vendor.restore_license(lic.license_id) is True
    assert vendor.restore_license(lic.license_id) is True
    assert vendor.get_license(lic.license_id).status == LicenseStatus.ACTIVE
    
    # 4. Cancel Twice
    assert vendor.cancel_license(lic.license_id) is True
    assert vendor.cancel_license(lic.license_id) is True
    assert vendor.get_license(lic.license_id).status == LicenseStatus.CANCELLED
    
    # 5. Revoke Twice
    assert vendor.revoke_license(lic.license_id) is True
    assert vendor.revoke_license(lic.license_id) is True
    assert vendor.get_license(lic.license_id).status == LicenseStatus.REVOKED

@pytest.mark.parametrize("i", range(1, 11))
def test_idempotent_renewals(vendor, i):
    cust = vendor.create_customer(f"Idem Cust {i}", f"idem_r_{i}@test.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    r1 = vendor.renew_license(lic.license_id, extension_days=30)
    r2 = vendor.renew_license(lic.license_id, extension_days=30)
    assert r1 is not None
    assert r2 is not None
