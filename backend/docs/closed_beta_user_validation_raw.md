# Saarthi — Closed Beta User Validation Raw Audit Log

**Audit Date**: August 20, 2026  
**Environment**: Physical Windows 11 Workstation  
**Mode**: Unedited First-Pass Raw User Journey Execution  

---

## Raw Execution Findings Across 27 End-to-End User Journey Steps

### 1. Launch & Hardware Profiling
- `GET /api/health` -> HTTP 200 `{'status': 'ok', 'service': 'saarthi'}` (PASS)
- `GET /api/ai/hardware` -> HTTP 200 `{'cpu': 'Intel64 Family 6 Model 165...', 'ram_gb': 23.8, 'gpu': 'NVIDIA GeForce GTX 1650 Ti', 'vram_gb': 4.0}` (PASS)

### 2. Nemotron Recommendation & Catalog Endpoints
- `GET /api/nemotron/recommendation` -> HTTP 200 `{'recommended_tier': 'SUPER', 'recommended_model': {'model_id': 'nemotron-3-nano:4b'}}` (PASS)
- `GET /api/ai/catalog` -> **UNHANDLED EXCEPTION / HTTP 500 CRASH**:
  ```text
  AttributeError: type object 'NemotronRecommendationService' has no attribute 'evaluate'
  File "E:\Saarthi\backend\app\api\routes.py", line 259, in get_nemotron_catalog_endpoint
      rec_result = NemotronRecommendationService.evaluate(capabilities)
  ```
  *Impact*: Calling `GET /api/ai/catalog` or `GET /api/ai/status` causes an unhandled 500 internal server error crash on the client UI.

### 3. Commercial Pricing Matrix Discrepancy
- `GET /api/billing/pricing-experiment?region=IN` -> HTTP 200:
  ```json
  {
    "currency": "INR",
    "free": 0,
    "student": 149,
    "personal": 399,
    "power": 799,
    "variant": "STUDENT_CONTROL_149"
  }
  ```
  *Impact*: The backend pricing experiment control variant returns `"student": 149`, whereas the updated commercial UI specification requires **Student ₹99** (INR) / **$1.50** (USD), **Personal ₹399** (INR) / **$5** (USD), **Power ₹799** (INR) / **$10** (USD).

### 4. Route Contract & Field Name Discrepancies
- `POST /api/career/cover-letter` requires explicit body keys `resume_text`, `company`, `role`, `job_description`. If generic keys (`resume`) are passed, FastAPI returns HTTP 422 Unprocessable Entity error.
- `POST /api/career/interview-prep` requires explicit body keys `resume_text`, `company`, `role`, `job_description`. Passing generic keys returns HTTP 422.

### 5. Summary of Raw Audit Status Codes
- `GET /api/health` -> HTTP 200 (OK)
- `GET /api/ai/hardware` -> HTTP 200 (OK)
- `GET /api/nemotron/recommendation` -> HTTP 200 (OK)
- `GET /api/ollama/diagnostics` -> HTTP 200 (OK)
- `GET /api/license/status` -> HTTP 200 (OK - Default `FREE` tier, watermark required)
- `GET /api/billing/pricing-experiment?region=IN` -> HTTP 200 (OK - Control variant returns 149)
- `GET /api/ai/catalog` -> **HTTP 500 Server Crash** (`AttributeError`)
- `GET /api/ai/status` -> **HTTP 500 Server Crash** (`AttributeError`)
