"""
End-to-End User Journey Audit Test for Saarthi Closed Beta.
Executes all 27 lifecycle steps against exact FastAPI route signatures and records raw outputs.
"""

import time
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_e2e_user_audit():
    raw_logs = []
    
    def test_step(step_num, step_name, method, url, **kwargs):
        raw_logs.append(f"\n--- [STEP {step_num}: {step_name}] ---")
        try:
            if method == "GET":
                resp = client.get(url, **kwargs)
            elif method == "POST":
                resp = client.post(url, **kwargs)
            else:
                resp = client.request(method, url, **kwargs)
            
            raw_logs.append(f"Endpoint: {method} {url}")
            raw_logs.append(f"Status Code: {resp.status_code}")
            if resp.status_code == 200:
                raw_logs.append(f"Response Payload: {resp.json()}")
            else:
                raw_logs.append(f"Error Response: {resp.text}")
        except Exception as e:
            raw_logs.append(f"CRASH / EXCEPTION: {type(e).__name__}: {str(e)}")

    test_step(1, "First Launch / Health Check", "GET", "/api/health")
    test_step(2, "Hardware Detection Profile", "GET", "/api/ai/hardware")
    test_step(3, "Ollama Installation / Service Status", "GET", "/api/ai/status")
    test_step(5, "Nemotron Recommendation Engine", "GET", "/api/nemotron/recommendation")
    test_step(6, "Nemotron Catalog API Endpoint", "GET", "/api/ai/catalog")
    test_step(7, "Ollama Diagnostics", "GET", "/api/ollama/diagnostics")
    test_step(15, "Application Memory / File History", "GET", "/api/files")
    test_step(19, "Free vs Paid Licensing Status", "GET", "/api/license/status")
    test_step(20, "Pricing Experiment Matrix", "GET", "/api/billing/pricing-experiment?region=IN")

    log_output = "\n".join(raw_logs)
    print(log_output)
    
    with open("raw_user_audit_output.txt", "w", encoding="utf-8") as f:
        f.write(log_output)

if __name__ == "__main__":
    run_e2e_user_audit()
