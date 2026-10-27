import pytest
import os
import tempfile
import json
from app.licensing.telemetry import PrivacySafeTelemetryLogger

def test_telemetry_sanitization():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = PrivacySafeTelemetryLogger(log_dir=tmpdir)
        
        sensitive_event_details = {
            "resume": "CONFIDENTIAL RESUME TEXT",
            "prompt": "SELECT * FROM users",
            "cover_letter": "DEAR HIRING MANAGER...",
            "email": "user@private.com",
            "feature_used": "ATS_MATCH",
            "doc_type": "tailored_resume",
            "watermarked": True
        }
        
        logger.log_event("DOCUMENT_GENERATED", sensitive_event_details)
        
        log_path = os.path.join(tmpdir, "operational_telemetry.log")
        assert os.path.exists(log_path)
        
        with open(log_path, "r", encoding="utf-8") as f:
            line = f.readline()
            data = json.loads(line)
            
            # Verify sensitive content keys were stripped
            details = data["details"]
            assert "resume" not in details
            assert "prompt" not in details
            assert "cover_letter" not in details
            assert "email" not in details
            
            # Verify allowed metadata keys were preserved
            assert details["feature_used"] == "ATS_MATCH"
            assert details["doc_type"] == "tailored_resume"
            assert details["watermarked"] is True
            assert data["privacy_guarantee"] == "ZERO_CUSTOMER_CONTENT_LOGGED"
