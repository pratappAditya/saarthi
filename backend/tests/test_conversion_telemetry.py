import pytest
from app.licensing.telemetry import PrivacySafeTelemetryLogger

def test_telemetry_event_logging_and_conversion_metrics():
    logger = PrivacySafeTelemetryLogger(log_dir="data/logs")
    logger.log_event("DOCUMENT_GENERATED", {"doc_type": "tailored_resume", "watermarked": True})
    logger.log_event("WATERMARKED_EXPORT", {"doc_type": "tailored_resume"})
    logger.log_event("PRICING_VIEWED")
    logger.log_event("CHECKOUT_STARTED")
    logger.log_event("PAYMENT_SUCCESS")

    metrics = logger.get_conversion_metrics()
    assert "metrics" in metrics
    assert "counts" in metrics
    assert metrics["privacy_guarantee"] == "Metrics computed strictly from operational metadata. Zero user content collected."
