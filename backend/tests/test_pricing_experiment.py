import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.licensing.watermark import WatermarkEngine

client = TestClient(app)

def test_pricing_experiment_variant_assignment():
    v1 = WatermarkEngine.get_pricing_experiment_variant("user_100")
    v2 = WatermarkEngine.get_pricing_experiment_variant("user_100")
    assert v1 == v2
    assert v1 in ["STUDENT_CONTROL_149", "STUDENT_TREATMENT_100"]

def test_pricing_experiment_endpoint_inr():
    res = client.get("/api/billing/pricing-experiment?user_id=test_user_inr&region=IN")
    assert res.status_code == 200
    data = res.json()
    assert data["currency"] == "INR"
    assert data["free"] == 0
    assert data["personal"] == 399
    assert data["power"] == 799
    assert data["student"] in [149, 100]

def test_pricing_experiment_endpoint_usd():
    res = client.get("/api/billing/pricing-experiment?user_id=test_user_usd&region=US")
    assert res.status_code == 200
    data = res.json()
    assert data["currency"] == "USD"
    assert data["free"] == 0
    assert data["student"] == 1.50
    assert data["personal"] == 5.00
    assert data["power"] == 10.00

def test_refund_request_flow_and_duplicate_prevention():
    from app.api.routes import vendor_instance
    from app.licensing.models import LicensePlan
    cust = vendor_instance.create_customer(name="Refund Candidate", email="refund@example.com")
    lic = vendor_instance.create_license(customer_id=cust.customer_id, plan=LicensePlan.STUDENT)
    license_id = lic.license_id

    # Submit refund request
    refund_res = client.post("/api/billing/refund-request", json={
        "user_id": "refund_test_user",
        "license_id": license_id,
        "reason": "24-hour satisfaction guarantee test"
    })
    assert refund_res.status_code == 200
    assert refund_res.json()["status"] == "ok"

    # Submit duplicate refund request
    dup_res = client.post("/api/billing/refund-request", json={
        "user_id": "refund_test_user",
        "license_id": license_id,
        "reason": "duplicate test"
    })
    assert dup_res.status_code == 400
    assert "already processed" in dup_res.json()["detail"]
