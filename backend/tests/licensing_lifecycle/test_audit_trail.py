import pytest
from app.licensing.models import LicensePlan
from app.licensing.vendor_server import VendorServer

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_complete_audit_trail_lifecycle(vendor):
    cust = vendor.create_customer("Audit User", "audit_trail@saarthi.ai", actor="admin_alice")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, actor="admin_alice")
    vendor.activate_license(lic.license_key, "fp_aud_1")
    vendor.suspend_license(lic.license_id, actor="admin_bob", reason="Non-payment")
    vendor.restore_license(lic.license_id, actor="admin_bob")
    vendor.renew_license(lic.license_id, extension_days=30, actor="admin_alice")
    vendor.change_entitlement(lic.license_id, LicensePlan.YEARLY, actor="admin_alice")
    vendor.revoke_license(lic.license_id, actor="admin_charlie", reason="Terms violation")
    
    logs = vendor.get_audit_logs(lic.license_id)
    actions = [l.action for l in logs]
    
    assert "CREATE_LICENSE" in actions
    assert "ACTIVATE_LICENSE" in actions
    assert "SUSPEND_LICENSE" in actions
    assert "RESTORE_LICENSE" in actions
    assert "RENEW_LICENSE" in actions
    assert "CHANGE_ENTITLEMENT" in actions
    assert "REVOKE_LICENSE" in actions
    
    # Audit log privacy verification
    for log in logs:
        assert log.actor in ("admin_alice", "admin_bob", "admin_charlie", "system", "client", "admin")
        details_str = str(log.details or "").lower()
        for forbidden in ["prompt", "message", "memory", "file", "chat"]:
            assert forbidden not in details_str

@pytest.mark.parametrize("i", range(1, 11))
def test_audit_logs_batch(vendor, i):
    cust = vendor.create_customer(f"User {i}", f"aud_b_{i}@test.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    vendor.suspend_license(lic.license_id, actor=f"actor_{i}")
    
    logs = vendor.get_audit_logs(lic.license_id)
    assert any(l.actor == f"actor_{i}" for l in logs)
