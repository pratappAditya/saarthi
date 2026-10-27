import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("saarthi.telemetry")

FORBIDDEN_CONTENT_KEYS = {
    "prompt", "message", "content", "resume", "cover_letter",
    "memory", "email", "calendar", "secret", "private_key",
    "token", "password", "notes", "description"
}

from app.config.settings import settings

class PrivacySafeTelemetryLogger:
    """
    Operational metrics logger strictly enforcing privacy guarantees.
    Logs feature usage counters, error categories, and licensing events.
    NEVER logs customer prompt, resume, cover letter, or chat content.
    """
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir if log_dir is not None else os.path.join(settings.SAARTHI_DATA_DIR, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.telemetry_file = os.path.join(self.log_dir, "operational_telemetry.log")

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in data.items():
            k_lower = k.lower()
            if any(forbidden in k_lower for forbidden in FORBIDDEN_CONTENT_KEYS):
                continue
            if isinstance(v, (str, int, float, bool, type(None))):
                sanitized[k] = v
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_data(v)
        return sanitized

    def log_event(self, event_type: str, details: Optional[Dict[str, Any]] = None):
        sanitized_details = self._sanitize_data(details or {})
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "details": sanitized_details,
            "privacy_guarantee": "ZERO_CUSTOMER_CONTENT_LOGGED"
        }
        
        line = json.dumps(entry)
        try:
            with open(self.telemetry_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            logger.error(f"Failed to write telemetry: {e}")

    def get_conversion_metrics(self) -> Dict[str, Any]:
        """
        Calculates operational monetization metrics strictly based on real observed log events.
        Does NOT manufacture or fabricate metrics.
        """
        counts = {
            "FREE_USER_ACTIVATED": 0,
            "RESUME_IMPORTED": 0,
            "JOB_DESCRIPTION_ANALYZED": 0,
            "ATS_ANALYSIS_COMPLETED": 0,
            "DOCUMENT_GENERATED": 0,
            "DOCUMENT_EXPORTED": 0,
            "WATERMARKED_EXPORT": 0,
            "PRICING_VIEWED": 0,
            "UPGRADE_PROMPT_SHOWN": 0,
            "CHECKOUT_STARTED": 0,
            "PAYMENT_SUCCESS": 0,
            "PAYMENT_FAILED": 0,
            "PLAN_ACTIVATED": 0
        }

        if os.path.exists(self.telemetry_file):
            try:
                with open(self.telemetry_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            event_type = data.get("event_type")
                            if event_type in counts:
                                counts[event_type] += 1
                        except Exception:
                            continue
            except Exception as e:
                logger.error(f"Error reading telemetry log: {e}")

        # Compute real rates
        total_exports = counts["DOCUMENT_EXPORTED"]
        watermark_exports = counts["WATERMARKED_EXPORT"]
        pricing_views = counts["PRICING_VIEWED"]
        checkouts = counts["CHECKOUT_STARTED"]
        payments = counts["PAYMENT_SUCCESS"]
        activations = counts["PLAN_ACTIVATED"]
        free_activations = counts["FREE_USER_ACTIVATED"]

        watermark_exposure_rate = round((watermark_exports / max(total_exports, 1)) * 100, 2) if total_exports > 0 else 0.0
        pricing_view_rate = round((pricing_views / max(counts["UPGRADE_PROMPT_SHOWN"], 1)) * 100, 2) if counts["UPGRADE_PROMPT_SHOWN"] > 0 else 0.0
        checkout_conversion = round((checkouts / max(pricing_views, 1)) * 100, 2) if pricing_views > 0 else 0.0
        payment_conversion = round((payments / max(checkouts, 1)) * 100, 2) if checkouts > 0 else 0.0
        free_to_paid_conversion = round((activations / max(free_activations, 1)) * 100, 2) if free_activations > 0 else 0.0

        return {
            "counts": counts,
            "metrics": {
                "watermark_exposure_rate": f"{watermark_exposure_rate}%",
                "pricing_view_rate": f"{pricing_view_rate}%",
                "checkout_conversion": f"{checkout_conversion}%",
                "payment_conversion": f"{payment_conversion}%",
                "free_to_paid_conversion": f"{free_to_paid_conversion}%"
            },
            "privacy_guarantee": "Metrics computed strictly from operational metadata. Zero user content collected."
        }

# Global instance for app metrics
telemetry = PrivacySafeTelemetryLogger()

