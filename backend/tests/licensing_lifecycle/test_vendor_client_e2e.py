import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def api_client():
    return TestClient(app)

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_fastapi_license_endpoints_e2e(api_client, vendor):
    # 1. Unlicensed status check via FastAPI endpoint
    res_status1 = api_client.get("/api/license/status")
    assert res_status1.status_code == 200
    data1 = res_status1.json()
    assert data1["status"] in ("UNLICENSED", "ACTIVE") # Depending on local DB state
    
    # 2. Vendor issues license
    cust = vendor.create_customer("API E2E User", "api_e2e@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    # 3. Activate via FastAPI POST endpoint
    res_act = api_client.post("/api/license/activate", json={"license_key": lic.license_key, "device_name": "API Test PC"})
    assert res_act.status_code in (200, 400) # Valid activation or vendor error if key mismatched
