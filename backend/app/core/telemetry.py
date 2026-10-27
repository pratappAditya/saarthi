import time
import threading
import psutil
import shutil
import os
from typing import Dict, Any
from app.config.settings import settings

class TelemetryCollector:
    """
    Thread-safe operational telemetry collector for Saarthi.
    Tracks HTTP request counts, status codes, latency histograms, tool executions, and AI model timings.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.start_time = time.time()
        self.total_requests = 0
        self.status_counts = {200: 0, 400: 0, 401: 0, 403: 0, 404: 0, 422: 0, 429: 0, 500: 0, 503: 0}
        self.total_latency_ms = 0.0
        self.active_requests = 0
        self.tool_execution_count = 0
        self.ai_call_count = 0
        self.ai_total_latency_ms = 0.0
        self.crash_reports_ingested = 0

    def record_request(self, status_code: int, latency_ms: float):
        with self._lock:
            self.total_requests += 1
            self.total_latency_ms += latency_ms
            if status_code in self.status_counts:
                self.status_counts[status_code] += 1
            else:
                self.status_counts[status_code] = 1

    def increment_active_requests(self):
        with self._lock:
            self.active_requests += 1

    def decrement_active_requests(self):
        with self._lock:
            self.active_requests = max(0, self.active_requests - 1)

    def record_tool_execution(self):
        with self._lock:
            self.tool_execution_count += 1

    def record_ai_call(self, latency_ms: float):
        with self._lock:
            self.ai_call_count += 1
            self.ai_total_latency_ms += latency_ms

    def record_crash_report(self):
        with self._lock:
            self.crash_reports_ingested += 1

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            uptime = round(time.time() - self.start_time, 2)
            avg_latency = round(self.total_latency_ms / self.total_requests, 2) if self.total_requests > 0 else 0.0
            avg_ai_latency = round(self.ai_total_latency_ms / self.ai_call_count, 2) if self.ai_call_count > 0 else 0.0

            # Hardware stats
            mem = psutil.virtual_memory()
            cpu_pct = psutil.cpu_percent(interval=None)
            total_d, used_d, free_d = shutil.disk_usage(settings.SAARTHI_DATA_DIR)

            return {
                "uptime_seconds": uptime,
                "total_requests": self.total_requests,
                "active_requests": self.active_requests,
                "average_latency_ms": avg_latency,
                "status_counts": self.status_counts,
                "tool_executions": self.tool_execution_count,
                "ai_calls": self.ai_call_count,
                "average_ai_latency_ms": avg_ai_latency,
                "crash_reports": self.crash_reports_ingested,
                "system": {
                    "cpu_percent": cpu_pct,
                    "memory_used_mb": round(mem.used / (1024 * 1024), 2),
                    "memory_percent": mem.percent,
                    "disk_free_gb": round(free_d / (1024**3), 2)
                }
            }

telemetry = TelemetryCollector()
