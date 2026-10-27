"""
Saarthi Ops Monitoring Collector (Hardened & Audited).
Collects real-time telemetry, enforces explicit scoping and measurement typing,
isolates unmeasured services from health scoring, and fail-closes on unavailable measurements.
"""

import os
import time
import shutil
import logging
import threading
import psutil
import urllib.request
import urllib.error
from collections import deque
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from app.config.settings import settings
from app.db.connection import get_db_connection
from app.core.telemetry import telemetry
from app.ops.config import (
    ALLOWED_OPS_SERVICES,
    MAX_ERROR_LOGS_LIMIT,
    DEFAULT_ERROR_LOGS_LIMIT,
    MAX_SNAPSHOTS_STORED
)
from app.ops.redactor import ops_redactor
from app.ops.authenticity import (
    snapshot_authenticity_service,
    FRESHNESS_WARN_SECONDS,
    FRESHNESS_EXPIRE_SECONDS
)

logger = logging.getLogger("app.ops.collector")

class OpsCollector:
    """
    Audited, thread-safe monitoring collector for Saarthi Ops.
    Explicitly labels host, container, and process telemetry scopes.
    Never presents unmeasured or simulated services as live verified observations.
    """

    def __init__(self):
        self._lock = threading.RLock()
        # In-memory circular buffer for sanitized recent application errors
        self._error_buffer: deque = deque(maxlen=100)
        # In-memory circular buffer for signed monitoring snapshot envelopes
        self._snapshot_buffer: deque = deque(maxlen=MAX_SNAPSHOTS_STORED)
        self.last_collection_timestamp: Optional[str] = None
        self._trusted_host_snapshot: Optional[Dict[str, Any]] = None

        # Populate initial signed snapshot
        self.create_snapshot()

    def record_error(
        self,
        message: str,
        level: str = "ERROR",
        source: str = "app.general",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingests an error into the Ops circular buffer after full secret redaction.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        sanitized_msg = ops_redactor.redact_text(message)
        sanitized_details = ops_redactor.redact_data(details or {})

        entry = {
            "timestamp": now_str,
            "level": level.upper(),
            "source": source,
            "message": sanitized_msg,
            "details": sanitized_details
        }
        self._error_buffer.append(entry)
        return entry

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Reads CPU, Memory, Disk, and Uptime metrics using safe standard libraries.
        Explicitly tags scope (host vs process) and measurement type.
        Fails safely to 'unavailable' if metrics cannot be accessed.
        """
        try:
            is_containerized = os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = os.cpu_count() or 1

            # Inspect cgroup memory limit if running inside container
            cgroup_mem_limit_bytes = None
            if is_containerized:
                for cg_path in ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
                    if os.path.exists(cg_path):
                        try:
                            with open(cg_path, "r") as f:
                                val = f.read().strip()
                                if val and val != "max" and int(val) < 9000000000000000000:
                                    cgroup_mem_limit_bytes = int(val)
                                    break
                        except Exception:
                            pass

            # Memory metrics (host visible vs cgroup)
            mem = psutil.virtual_memory()
            ram_info = {
                "total_mb": round(mem.total / (1024 * 1024), 2),
                "available_mb": round(mem.available / (1024 * 1024), 2),
                "used_mb": round(mem.used / (1024 * 1024), 2),
                "percent_used": mem.percent,
                "scope": "container_cgroup" if cgroup_mem_limit_bytes else ("host_visible_unisolated" if is_containerized else "host"),
                "cgroup_limit_mb": round(cgroup_mem_limit_bytes / (1024 * 1024), 2) if cgroup_mem_limit_bytes else None,
                "measurement_type": "live_probe"
            }

            # Disk metrics (Container volume vs Host filesystem)
            data_dir = getattr(settings, "SAARTHI_DATA_DIR", os.getcwd())
            if not os.path.exists(data_dir):
                data_dir = os.getcwd()
            total_d, used_d, free_d = shutil.disk_usage(data_dir)
            disk_info = {
                "total_gb": round(total_d / (1024 * 1024 * 1024), 2),
                "free_gb": round(free_d / (1024 * 1024 * 1024), 2),
                "used_gb": round(used_d / (1024 * 1024 * 1024), 2),
                "percent_used": round((used_d / total_d) * 100, 2) if total_d > 0 else 0.0,
                "scope": "container_volume" if is_containerized else "host",
                "volume_path": data_dir,
                "measurement_type": "live_probe"
            }

            # Uptime (Process vs Host)
            proc_uptime_sec = round(time.time() - telemetry.start_time, 2)
            boot_time = psutil.boot_time()
            system_uptime_sec = round(time.time() - boot_time, 2)

            return {
                "status": "available",
                "scope": "container_and_process" if is_containerized else "host_and_process",
                "is_containerized": is_containerized,
                "measurement_type": "live_probe",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cpu": {
                    "percent_used": cpu_percent,
                    "logical_cores": cpu_count,
                    "scope": "host_shared" if is_containerized else "host"
                },
                "ram": ram_info,
                "disk": disk_info,
                "uptime": {
                    "process_seconds": proc_uptime_sec,
                    "system_seconds": system_uptime_sec
                },
                "active_requests": telemetry.active_requests,
                "total_requests": telemetry.total_requests
            }
        except Exception as e:
            logger.warning(f"Error collecting system metrics: {e}")
            return {
                "status": "unavailable",
                "scope": "host",
                "measurement_type": "unavailable",
                "reason": f"Hardware/OS metric collection failed: {e}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """
        Probes a single allowlisted service.
        Explicitly identifies measurement type (live_probe vs in_process vs unmeasured).
        Does NOT inject fabricated latencies.
        """
        clean_id = service_id.strip().lower()
        if clean_id not in ALLOWED_OPS_SERVICES:
            raise HTTPException(
                status_code=400,
                detail=f"Service '{service_id}' is not in the permitted Saarthi Ops allowlist."
            )

        now_str = datetime.now(timezone.utc).isoformat()

        if clean_id == "saarthi-backend":
            # In-process probe: backend is currently executing this code
            return {
                "service_id": "saarthi-backend",
                "name": "Saarthi FastAPI Backend",
                "status": "ONLINE",
                "scope": "process",
                "measurement_type": "in_process",
                "is_verified": True,
                "latency_ms": None,
                "version": "0.5.0-rc2",
                "last_checked": now_str
            }

        elif clean_id == "saarthi-db":
            # Live database connectivity & integrity probe
            db_status = "UNKNOWN"
            integrity = "UNKNOWN"
            start_t = time.time()
            try:
                with get_db_connection() as conn:
                    check = conn.execute("PRAGMA integrity_check").fetchone()
                    integrity = check[0] if check else "FAILED"
                    db_status = "ONLINE" if integrity.lower() == "ok" else "DEGRADED"
                latency = round((time.time() - start_t) * 1000, 2)
            except Exception as e:
                db_status = "OFFLINE"
                integrity = f"ERROR: {ops_redactor.redact_text(str(e))}"
                latency = round((time.time() - start_t) * 1000, 2)

            return {
                "service_id": "saarthi-db",
                "name": "Saarthi Database Engine",
                "status": db_status,
                "scope": "process",
                "measurement_type": "live_probe",
                "is_verified": True,
                "integrity": integrity,
                "latency_ms": latency,
                "last_checked": now_str
            }

        elif clean_id == "ollama":
            # Live HTTP socket probe to Ollama base URL
            ollama_url = f"{settings.OLLAMA_BASE_URL}/api/tags"
            start_t = time.time()
            try:
                req = urllib.request.Request(ollama_url, method="GET")
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    latency = round((time.time() - start_t) * 1000, 2)
                    if resp.status == 200:
                        return {
                            "service_id": "ollama",
                            "name": "Ollama Local AI Engine",
                            "status": "ONLINE",
                            "scope": "process",
                            "measurement_type": "live_probe",
                            "is_verified": True,
                            "latency_ms": latency,
                            "endpoint": settings.OLLAMA_BASE_URL,
                            "last_checked": now_str
                        }
                    return {
                        "service_id": "ollama",
                        "name": "Ollama Local AI Engine",
                        "status": "DEGRADED",
                        "scope": "process",
                        "measurement_type": "live_probe",
                        "is_verified": True,
                        "latency_ms": latency,
                        "endpoint": settings.OLLAMA_BASE_URL,
                        "last_checked": now_str
                    }
            except Exception:
                latency = round((time.time() - start_t) * 1000, 2)
                return {
                    "service_id": "ollama",
                    "name": "Ollama Local AI Engine",
                    "status": "OFFLINE",
                    "scope": "process",
                    "measurement_type": "live_probe",
                    "is_verified": True,
                    "latency_ms": latency,
                    "endpoint": settings.OLLAMA_BASE_URL,
                    "last_checked": now_str
                }

        elif clean_id in ("saarthi-frontend", "saarthi-admin"):
            # Static SPA frontend assets: In local mode or standalone backend,
            # this cannot be actively probed unless a separate webserver port is actively verified.
            # Label honestly as UNMEASURED so it does not fabricate health status or latency.
            return {
                "service_id": clean_id,
                "name": "Saarthi User App SPA" if clean_id == "saarthi-frontend" else "Saarthi Admin Control Plane",
                "status": "UNMEASURED",
                "scope": "container",
                "measurement_type": "unmeasured",
                "is_verified": False,
                "latency_ms": None,
                "last_checked": now_str,
                "note": "Static web assets unprobed; omitted from health calculation."
            }

        raise HTTPException(status_code=400, detail=f"Unsupported service: {service_id}")

    def get_all_services(self) -> List[Dict[str, Any]]:
        """Probes all allowlisted Saarthi services."""
        return [self.get_service_health(s) for s in sorted(ALLOWED_OPS_SERVICES)]

    def get_recent_errors(self, limit: int = DEFAULT_ERROR_LOGS_LIMIT) -> List[Dict[str, Any]]:
        """
        Returns recent sanitized application errors bounded by MAX_ERROR_LOGS_LIMIT.
        """
        safe_limit = min(max(1, limit), MAX_ERROR_LOGS_LIMIT)
        errors = list(self._error_buffer)
        return errors[-safe_limit:]

    def sync_host_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Synchronizes and ingests the host collector snapshot from disk.
        Separates one-time ingestion from repeated dashboard reads:
        - If file content matches the already verified trusted snapshot, returns it without re-verifying.
        - If file has a new envelope, authenticates it, records nonce/watermark, and updates trusted state.
        - If invalid, replayed, or out-of-order, rejects it and preserves current trusted state.
        """
        host_snap_path = os.getenv("SAARTHI_HOST_SNAPSHOT_FILE", "/opt/saarthi-staging/telemetry/live_snapshot.json")
        if not os.path.exists(host_snap_path) or not os.path.isfile(host_snap_path):
            return self._trusted_host_snapshot

        with self._lock:
            try:
                import json
                with open(host_snap_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    return self._trusted_host_snapshot
                envelope = json.loads(content)
            except Exception as e:
                logger.warning(f"Error reading host snapshot file {host_snap_path}: {e}")
                return self._trusted_host_snapshot

            if not isinstance(envelope, dict):
                logger.warning(f"Malformed envelope in {host_snap_path}")
                return self._trusted_host_snapshot

            nonce = envelope.get("nonce")
            if not nonce:
                return self._trusted_host_snapshot

            # 1. Check if already active trusted snapshot in memory
            if self._trusted_host_snapshot and self._trusted_host_snapshot.get("nonce") == nonce:
                return self._trusted_host_snapshot

            # 2. Check if this nonce was previously recorded in persistent store (e.g. across restart)
            source_id = envelope.get("source_id", "saarthi-ops-collector")
            persisted = snapshot_authenticity_service.replay_store.get_trusted_snapshot(source_id)
            if persisted and persisted.get("nonce") == nonce:
                self._trusted_host_snapshot = persisted
                return self._trusted_host_snapshot

            # 3. New candidate envelope: Authenticate and ingest atomically
            is_valid, reason, meta = snapshot_authenticity_service.verify_envelope(envelope)
            if is_valid and isinstance(envelope.get("payload"), dict):
                self._trusted_host_snapshot = envelope
                self._snapshot_buffer.append(envelope)
                logger.info(f"Successfully ingested and verified host snapshot (nonce={nonce}, freshness={meta.get('freshness')})")
                return self._trusted_host_snapshot
            else:
                logger.warning(f"Host snapshot rejected during ingestion from {host_snap_path}: {reason}")
                return self._trusted_host_snapshot

    def register_verified_snapshot(self, envelope: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> None:
        """Stores an externally verified snapshot into memory buffer and trusted host slot if applicable."""
        with self._lock:
            self._snapshot_buffer.append(envelope)
            source_id = envelope.get("source_id", "")
            if "host" in source_id or source_id == "saarthi-ops-collector":
                self._trusted_host_snapshot = envelope

    def get_container_status(self) -> Dict[str, Any]:
        """
        Restricted read-only container status reporter.
        Reads from the persistent verified trusted snapshot without re-consuming nonces.
        Direct Docker socket access (/var/run/docker.sock) is strictly blocked by security policy.
        Never executes Docker commands or invents fictitious container states.
        """
        now_ts = time.time()
        now_str = datetime.now(timezone.utc).isoformat()

        # Check and sync host snapshot if file updated
        trusted_snap = self.sync_host_snapshot() or self._trusted_host_snapshot
        if trusted_snap and isinstance(trusted_snap.get("payload"), dict):
            # Evaluate freshness of the trusted snapshot
            ts_str = trusted_snap.get("timestamp", "")
            try:
                if ts_str.endswith("Z"):
                    ts_str = ts_str[:-1] + "+00:00"
                snap_time = datetime.fromisoformat(ts_str)
                age_seconds = now_ts - snap_time.timestamp()
            except Exception:
                age_seconds = 99999.0

            if age_seconds > FRESHNESS_EXPIRE_SECONDS:
                freshness = "expired"
                status = "unavailable"
            elif age_seconds > FRESHNESS_WARN_SECONDS:
                freshness = "stale"
                status = "available"
            else:
                freshness = "fresh"
                status = "available"

            raw_containers = trusted_snap["payload"].get("containers", [])
            filtered_containers = [
                c for c in raw_containers
                if isinstance(c, dict) and (c.get("name") in ALLOWED_OPS_SERVICES or any(s in str(c.get("name")) for s in ("saarthi", "backend", "db", "frontend", "admin")))
            ]

            return {
                "status": status,
                "scope": "container",
                "measurement_type": "live_probe" if status == "available" else "expired",
                "source": "host_collector",
                "freshness": freshness,
                "age_seconds": round(age_seconds, 2),
                "timestamp": trusted_snap.get("timestamp"),
                "containers": filtered_containers if status == "available" else []
            }

        is_containerized = os.path.exists("/.dockerenv")
        if not is_containerized:
            return {
                "status": "unavailable",
                "scope": "container",
                "measurement_type": "unmeasured",
                "reason": "Container runtime not attached in local development mode",
                "freshness": "unavailable",
                "timestamp": now_str,
                "containers": []
            }

        # If containerized, report unavailable for direct Docker socket queries to reflect policy
        return {
            "status": "unavailable",
            "scope": "container",
            "measurement_type": "unmeasured",
            "reason": "Docker socket (/var/run/docker.sock) omitted by least-privilege security policy",
            "freshness": "unavailable",
            "timestamp": now_str,
            "containers": []
        }

    def create_snapshot(self) -> Dict[str, Any]:
        """
        Creates an immutable, cryptographically signed snapshot of current monitoring state.
        Enforces strict fail-closed health evaluation rules.
        """
        metrics = self.get_system_metrics()
        services = self.get_all_services()
        errors = self.get_recent_errors(limit=5)
        now_str = datetime.now(timezone.utc).isoformat()
        self.last_collection_timestamp = now_str

        # --- FAIL-CLOSED HEALTH EVALUATION RULES ---
        # 1. Check metric availability: Unavailable metrics MUST prevent healthy status
        metrics_available = (metrics.get("status") == "available")
        
        # 2. Database verification: Must be ONLINE
        db_service = next((s for s in services if s.get("service_id") == "saarthi-db"), None)
        db_online = bool(db_service and db_service.get("status") == "ONLINE")

        # 3. Verified services check: Only consider verified live probes
        verified_services = [s for s in services if s.get("is_verified") and s.get("service_id") != "ollama"]
        all_verified_online = all(s.get("status") == "ONLINE" for s in verified_services)

        cpu_usage = metrics.get("cpu", {}).get("percent_used", 0) if metrics_available else 0
        ram_usage = metrics.get("ram", {}).get("percent_used", 0) if metrics_available else 0

        # 4. Check host collector container telemetry if present
        container_status = self.get_container_status()
        container_expired = (
            container_status.get("source") == "host_collector" and
            container_status.get("freshness") == "expired"
        )

        if not db_online or (metrics_available and (cpu_usage > 95 or ram_usage > 95)):
            overall = "unhealthy"
        elif not metrics_available or container_expired:
            # Unavailable or expired telemetry CANNOT produce healthy status
            overall = "degraded"
        elif not all_verified_online or cpu_usage > 80 or ram_usage > 85:
            overall = "degraded"
        else:
            overall = "healthy"

        raw_payload = {
            "snapshot_id": f"ops_snap_{int(time.time() * 1000)}",
            "timestamp": now_str,
            "overall_health": overall,
            "metrics": metrics,
            "services": services,
            "recent_errors_count": len(self._error_buffer),
            "recent_errors_sample": errors,
            "evaluation_guarantee": "FAIL_CLOSED_AUTHENTIC"
        }

        # Cryptographically sign snapshot envelope
        signed_envelope = snapshot_authenticity_service.sign_snapshot(
            payload=raw_payload,
            source_id="saarthi-ops-collector-local"
        )
        self._snapshot_buffer.append(signed_envelope)
        return signed_envelope

    def get_snapshots(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns recent signed monitoring snapshot envelopes."""
        safe_limit = min(max(1, limit), MAX_SNAPSHOTS_STORED)
        return list(self._snapshot_buffer)[-safe_limit:]

    def get_incidents(self) -> List[Dict[str, Any]]:
        """
        Analyzes live verified telemetry to detect active or recent infrastructure incidents.
        Omitted from considering unmeasured static services.
        """
        incidents = []
        services = self.get_all_services()
        metrics = self.get_system_metrics()
        now_str = datetime.now(timezone.utc).isoformat()

        # Check DB
        for s in services:
            if s.get("service_id") == "saarthi-db" and s.get("status") != "ONLINE":
                incidents.append({
                    "incident_id": f"inc_db_{int(time.time())}",
                    "severity": "CRITICAL",
                    "title": "Database Engine Degraded or Offline",
                    "affected_service": "saarthi-db",
                    "detected_at": now_str,
                    "evidence": s.get("integrity", "Integrity check failed"),
                    "status": "ACTIVE"
                })

        # Check Ollama
        for s in services:
            if s.get("service_id") == "ollama" and s.get("status") == "OFFLINE":
                incidents.append({
                    "incident_id": f"inc_ollama_{int(time.time())}",
                    "severity": "WARNING",
                    "title": "Ollama Local AI Engine Unreachable",
                    "affected_service": "ollama",
                    "detected_at": now_str,
                    "evidence": f"Failed connection to {settings.OLLAMA_BASE_URL}",
                    "status": "ACTIVE"
                })

        # Check Memory & Disk
        if metrics.get("status") == "available":
            ram_pct = metrics.get("ram", {}).get("percent_used", 0)
            if ram_pct > 90:
                incidents.append({
                    "incident_id": f"inc_mem_{int(time.time())}",
                    "severity": "CRITICAL",
                    "title": "Host RAM Utilization Exceeds 90%",
                    "affected_service": "saarthi-backend",
                    "detected_at": now_str,
                    "evidence": f"RAM usage is {ram_pct}%",
                    "status": "ACTIVE"
                })

            disk_pct = metrics.get("disk", {}).get("percent_used", 0)
            if disk_pct > 90:
                incidents.append({
                    "incident_id": f"inc_disk_{int(time.time())}",
                    "severity": "CRITICAL",
                    "title": "Host Disk Utilization Exceeds 90%",
                    "affected_service": "saarthi-backend",
                    "detected_at": now_str,
                    "evidence": f"Disk usage is {disk_pct}%",
                    "status": "ACTIVE"
                })
        else:
            incidents.append({
                "incident_id": f"inc_telemetry_{int(time.time())}",
                "severity": "WARNING",
                "title": "Host Telemetry Measurements Unavailable",
                "affected_service": "saarthi-backend",
                "detected_at": now_str,
                "evidence": metrics.get("reason", "Metrics collection failed"),
                "status": "ACTIVE"
            })

        return incidents

    def get_overall_ops_health(self) -> Dict[str, Any]:
        """
        Returns top-level Ops health indicator, freshness classification,
        service summary, and active incidents count.
        Enforces standardized freshness policy (warn at 60s, expire at 180s).
        """
        signed_snap = self.create_snapshot()
        raw_payload = signed_snap["payload"]
        incidents = self.get_incidents()

        # Check freshness
        now = time.time()
        try:
            ts_str = signed_snap["timestamp"]
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            snap_time = datetime.fromisoformat(ts_str)
            age_seconds = now - snap_time.timestamp()
        except Exception:
            age_seconds = 0.0

        if age_seconds > FRESHNESS_EXPIRE_SECONDS:
            freshness = "expired"
            overall_status = "unavailable"
        elif age_seconds > FRESHNESS_WARN_SECONDS:
            freshness = "stale"
            overall_status = raw_payload["overall_health"]
        else:
            freshness = "fresh"
            overall_status = raw_payload["overall_health"]

        # EXPIRED TELEMETRY GUARANTEE:
        # If host collector telemetry is present but expired, overall status CANNOT be healthy
        container_status = self.get_container_status()
        if container_status.get("source") == "host_collector" and container_status.get("freshness") == "expired":
            if overall_status == "healthy":
                overall_status = "degraded"
            freshness = "expired"

        return {
            "status": overall_status,
            "freshness": freshness,
            "age_seconds": round(age_seconds, 2),
            "timestamp": signed_snap["timestamp"],
            "last_collection_timestamp": self.last_collection_timestamp,
            "services_count": len(raw_payload["services"]),
            "services_verified_online": sum(1 for s in raw_payload["services"] if s.get("status") == "ONLINE" and s.get("is_verified")),
            "services_unmeasured": sum(1 for s in raw_payload["services"] if not s.get("is_verified")),
            "active_incidents_count": len(incidents),
            "recent_errors_count": len(self._error_buffer),
            "signature": signed_snap["signature"]
        }

ops_collector = OpsCollector()
