import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings

client = TestClient(app)

@pytest.fixture
def admin_headers():
    # Login with admin master key
    key = getattr(settings, "VENDOR_ADMIN_KEY", None) or os.getenv("VENDOR_ADMIN_KEY", "")
    res = client.post("/admin/auth/login", json={"admin_key": key})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_admin_auth_flow(admin_headers):
    # Verify session
    verify_res = client.get("/admin/auth/verify", headers=admin_headers)
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["authenticated"] is True
    assert data["admin"]["role"] == "SUPER_ADMIN"

    # Test unauthorized access without token
    unauth_res = client.get("/admin/users")
    assert unauth_res.status_code in [401, 403]

def test_admin_dashboard_and_version(admin_headers):
    dash_res = client.get("/admin/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200
    metrics = dash_res.json()["metrics"]
    assert "total_users" in metrics

    ver_res = client.get("/admin/version", headers=admin_headers)
    assert ver_res.status_code == 200
    assert "version" in ver_res.json()

def test_admin_users_operations(admin_headers):
    # List users
    users_res = client.get("/admin/users", headers=admin_headers)
    assert users_res.status_code == 200
    users = users_res.json().get("users", [])
    assert isinstance(users, list)

def test_admin_organizations_operations(admin_headers):
    # List organizations
    orgs_res = client.get("/admin/organizations", headers=admin_headers)
    assert orgs_res.status_code == 200
    orgs = orgs_res.json().get("organizations", [])
    assert isinstance(orgs, list)

    if orgs:
        test_org_id = orgs[0]["org_id"]
        # Get details
        detail_res = client.get(f"/admin/organizations/{test_org_id}", headers=admin_headers)
        assert detail_res.status_code == 200
        assert "members" in detail_res.json()["organization"]

        # Update seats
        seats_res = client.post(
            f"/admin/organizations/{test_org_id}/seats",
            headers=admin_headers,
            json={"max_seats": 25}
        )
        assert seats_res.status_code == 200
        assert seats_res.json()["max_seats"] == 25

def test_admin_plans_and_entitlements(admin_headers):
    catalog_res = client.get("/admin/plans/catalog", headers=admin_headers)
    assert catalog_res.status_code == 200
    catalog = catalog_res.json()["catalog"]
    assert len(catalog) >= 5
    plan_ids = [p["id"].upper() for p in catalog]
    assert "FREE" in plan_ids
    assert "POWER" in plan_ids

def test_admin_billing_records(admin_headers):
    # Subscriptions
    subs_res = client.get("/admin/billing/subscriptions", headers=admin_headers)
    assert subs_res.status_code == 200

    # Payments
    pays_res = client.get("/admin/billing/payments", headers=admin_headers)
    assert pays_res.status_code == 200

    # Invoices
    inv_res = client.get("/admin/billing/invoices", headers=admin_headers)
    assert inv_res.status_code == 200

    # Refunds
    ref_res = client.get("/admin/billing/refunds", headers=admin_headers)
    assert ref_res.status_code == 200

    # Webhooks
    wh_res = client.get("/admin/billing/webhooks", headers=admin_headers)
    assert wh_res.status_code == 200

def test_admin_automations_and_routines(admin_headers):
    auto_res = client.get("/admin/automations", headers=admin_headers)
    assert auto_res.status_code == 200
    assert "automations" in auto_res.json()
    assert "routines" in auto_res.json()

def test_admin_research_operations(admin_headers):
    res_ov = client.get("/admin/research/overview", headers=admin_headers)
    assert res_ov.status_code == 200
    data = res_ov.json()
    assert data["total_domains"] == 17
    assert len(data["domains"]) == 17

    runs_res = client.get("/admin/research/runs", headers=admin_headers)
    assert runs_res.status_code == 200
    assert "runs" in runs_res.json()

def test_admin_system_health_and_db_check(admin_headers):
    health_res = client.get("/admin/health", headers=admin_headers)
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    db_res = client.post("/admin/health/db-check", headers=admin_headers)
    assert db_res.status_code == 200
    assert db_res.json()["integrity_check"] == "ok"

def test_admin_settings_feature_flags_and_tools(admin_headers):
    flags_res = client.get("/admin/feature-flags", headers=admin_headers)
    assert flags_res.status_code == 200
    assert "flags" in flags_res.json()

    tools_res = client.get("/admin/tools", headers=admin_headers)
    assert tools_res.status_code == 200
    assert "tools" in tools_res.json()

def test_admin_logout(admin_headers):
    logout_res = client.post("/admin/auth/logout", headers=admin_headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] in ["ok", "success"]
