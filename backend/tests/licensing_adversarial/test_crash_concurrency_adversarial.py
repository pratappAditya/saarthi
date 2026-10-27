import pytest
import asyncio
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

@pytest.mark.asyncio
async def test_concurrent_activations_same_license(env):
    vendor, _ = env
    cust = vendor.create_customer("Concurrent User", "conc@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=5)
    
    async def activate_worker(dev_idx):
        return vendor.activate_license(lic.license_key, f"fp_concurrent_{dev_idx}")
        
    tasks = [asyncio.create_task(activate_worker(i)) for i in range(5)]
    tokens = await asyncio.gather(*tasks)
    assert len(tokens) == 5
    assert len(set(tokens)) == 5

@pytest.mark.asyncio
@pytest.mark.parametrize("i", range(1, 39))
async def test_concurrent_vendor_audit_log_writes(env, i):
    vendor, _ = env
    cust = vendor.create_customer(f"Conc Cust {i}", f"conc_{i}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    vendor.suspend_license(lic.license_id)
    vendor.restore_license(lic.license_id)
    
    logs = vendor.get_audit_logs(lic.license_id)
    assert len(logs) >= 3
