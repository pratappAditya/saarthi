"""
Saarthi Ops AI-Assisted Diagnostic Engine.
Read-Only analysis of sanitized monitoring snapshots and error logs.
Zero execution capabilities: Strictly generates human-facing recommendations with no shell,
SSH, database write, or container mutation tooling.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from app.models.factory import ModelFactory
from app.ops.redactor import ops_redactor

logger = logging.getLogger("app.ops.diagnostics")

DISCLAIMER_TEXT = (
    "DISCLAIMER: All diagnostic outputs are advisory recommendations for human operator review. "
    "Saarthi Ops is strictly read-only and possesses NO execution, terminal, shell, or container mutation permissions."
)

class OpsDiagnosticEngine:
    """
    Read-only AI diagnostic reasoning service.
    Analyzes sanitized snapshots to produce structured diagnoses distinguishing facts from hypotheses.
    """

    @classmethod
    def diagnose_snapshot(
        cls,
        snapshot: Dict[str, Any],
        recent_errors: List[Dict[str, Any]],
        incident_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs diagnostic reasoning over sanitized telemetry.
        Tries local model gateway first; falls back cleanly to deterministic expert rules
        so Ops never fails if Ollama or the local model is offline.
        """
        # Ensure input data is fully sanitized
        clean_snapshot = ops_redactor.redact_data(snapshot)
        clean_errors = ops_redactor.redact_data(recent_errors)
        clean_incident = ops_redactor.redact_data(incident_context or {})

        # 1. Attempt AI analysis via ModelFactory if configured and online
        try:
            ai_result = cls._run_ai_model_analysis(clean_snapshot, clean_errors, clean_incident)
            if ai_result:
                return ai_result
        except Exception as e:
            logger.info(f"AI model unavailable for Ops diagnostics, falling back to deterministic expert engine: {e}")

        # 2. Deterministic Expert Rules Engine (Fail-safe, guaranteed availability)
        return cls._run_deterministic_diagnosis(clean_snapshot, clean_errors, clean_incident)

    @classmethod
    def _run_ai_model_analysis(
        cls,
        snapshot: Dict[str, Any],
        recent_errors: List[Dict[str, Any]],
        incident_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Queries the model gateway using a strict read-only prompt requesting structured JSON.
        """
        provider = ModelFactory.get_provider()
        if not provider or getattr(provider, "is_mock", False):
            # If mock provider, use deterministic engine for realistic operational output
            return None

        prompt = (
            "You are Saarthi Ops Diagnostic Assistant. You have READ-ONLY monitoring access.\n"
            "Analyze the following operational snapshot and errors. Respond ONLY in valid JSON.\n"
            "Required keys: problem_summary, facts, hypotheses, evidence, missing_evidence, "
            "confidence, safe_investigation_steps, shared_infrastructure_impact.\n\n"
            f"Snapshot: {json.dumps(snapshot, indent=2)}\n"
            f"Recent Errors: {json.dumps(recent_errors, indent=2)}\n"
            f"Incident: {json.dumps(incident_context, indent=2)}\n"
        )

        response = provider.generate(prompt=prompt, system_prompt="Strict JSON read-only diagnostic auditor.")
        if response and isinstance(response, str):
            clean_resp = response.strip()
            if clean_resp.startswith("```json"):
                clean_resp = clean_resp.split("```json")[1].split("```")[0].strip()
            elif clean_resp.startswith("```"):
                clean_resp = clean_resp.split("```")[1].split("```")[0].strip()
            
            data = json.loads(clean_resp)
            data["recommendations_disclaimer"] = DISCLAIMER_TEXT
            data["diagnostic_mode"] = "AI_MODEL_ASSISTED"
            return data

        return None

    @classmethod
    def _run_deterministic_diagnosis(
        cls,
        snapshot: Dict[str, Any],
        recent_errors: List[Dict[str, Any]],
        incident_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deterministic expert system diagnosing infrastructure state without hallucination.
        Distinguishes verified facts from unproven hypotheses and assesses shared VPS impact.
        """
        services = snapshot.get("services", [])
        metrics = snapshot.get("metrics", {})
        overall = snapshot.get("overall_health", "healthy")

        facts = []
        hypotheses = []
        evidence = []
        missing_evidence = []
        safe_steps = []
        shared_impact = []
        confidence = "HIGH"

        # Check snapshot freshness
        freshness = snapshot.get("freshness")
        if freshness in ("expired", "stale") or snapshot.get("is_stale"):
            facts.append(f"Telemetry snapshot freshness status is '{freshness}'.")
            missing_evidence.append("Active fresh host collector telemetry is missing or expired (> 180s).")
            if freshness == "expired" and overall == "healthy":
                overall = "degraded"
            confidence = "MEDIUM"

        # Evaluate Services
        offline_services = [s for s in services if s.get("status") in ("OFFLINE", "DEGRADED")]
        for s in services:
            s_id = s.get("service_id")
            status = s.get("status")
            facts.append(f"Service '{s_id}' state is {status} (latency: {s.get('latency_ms', 0)}ms).")
            if status != "ONLINE":
                evidence.append(f"Service check failure for {s_id}: status={status}, details={s.get('integrity', 'N/A')}")

        if offline_services:
            for os in offline_services:
                s_id = os.get("service_id")
                if s_id == "ollama":
                    hypotheses.append("Ollama daemon may not be started, or model weights have not finished loading.")
                    safe_steps.append("Check local service status: verify if Ollama process is active on port 11434.")
                    safe_steps.append("Inspect Ollama daemon system log using read-only journal/log viewer.")
                elif s_id == "saarthi-db":
                    hypotheses.append("Database lock contention or SQLite file corruption detected.")
                    safe_steps.append("Run read-only database integrity verification: PRAGMA integrity_check.")
                    safe_steps.append("Verify disk storage space and file permissions on database volume.")

        # Evaluate System Metrics
        if metrics.get("status") == "available":
            cpu = metrics.get("cpu", {}).get("percent_used", 0)
            ram = metrics.get("ram", {}).get("percent_used", 0)
            disk = metrics.get("disk", {}).get("percent_used", 0)

            facts.append(f"CPU utilization is {cpu}%, RAM utilization is {ram}%, Disk utilization is {disk}%.")

            if ram > 85:
                evidence.append(f"RAM utilization high: {ram}% consumed.")
                hypotheses.append("High memory usage may trigger OS OOM killer or degrade co-located applications.")
                safe_steps.append("Inspect per-process memory consumption using top/ps in read-only mode.")
                shared_impact.append(
                    "CRITICAL SHARED HOST IMPACT: Memory exhaustion on shared VPS (<HOST_IP>) "
                    "risks triggering the Linux OOM killer against co-located enterprise workloads containers or databases."
                )
            if disk > 85:
                evidence.append(f"Disk utilization high: {disk}% consumed.")
                hypotheses.append("Disk space exhaustion prevents database write-ahead logging and temporary file creation.")
                safe_steps.append("Inspect disk usage by directory (du -sh) without deleting files.")
                shared_impact.append(
                    "CRITICAL SHARED HOST IMPACT: Low disk space on root volume will cause co-located enterprise workloads database "
                    "transactions to fail and stall ERP operations."
                )
        else:
            missing_evidence.append("Host OS hardware telemetry was unavailable at time of collection.")
            confidence = "MEDIUM"

        # Evaluate Recent Errors
        if recent_errors:
            error_count = len(recent_errors)
            facts.append(f"Detected {error_count} sanitized application error events in recent log window.")
            for err in recent_errors[-3:]:
                evidence.append(f"[{err.get('level')}] {err.get('source')}: {err.get('message')}")
        else:
            facts.append("Zero unhandled application errors detected in current window.")

        # Default shared host assessment if no alerts
        if not shared_impact:
            shared_impact.append(
                "NORMAL: Current resource footprint is stable. No adverse impact detected on shared host or co-located co-located enterprise workloads."
            )

        if not missing_evidence:
            missing_evidence.append("Container-level cgroup metrics not attached in local development mode.")

        if not safe_steps:
            safe_steps.append("Continue standard passive telemetry observation. No intervention required.")

        summary = (
            f"System is operating in a {overall.upper()} state. "
            f"{len(offline_services)} services degraded/offline. "
            f"{len(recent_errors)} recent error events logged."
        )

        return {
            "problem_summary": summary,
            "overall_health": overall,
            "facts": facts,
            "hypotheses": hypotheses if hypotheses else ["System behavior is within expected nominal operating parameters."],
            "evidence": evidence if evidence else ["All allowlisted service probes and telemetry metrics report nominal status."],
            "missing_evidence": missing_evidence,
            "confidence": confidence,
            "safe_investigation_steps": safe_steps,
            "shared_infrastructure_impact": shared_impact,
            "recommendations_disclaimer": DISCLAIMER_TEXT,
            "diagnostic_mode": "DETERMINISTIC_EXPERT_SYSTEM"
        }

ops_diagnostic_engine = OpsDiagnosticEngine()
