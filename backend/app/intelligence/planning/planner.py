import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.intelligence.planning.task_graph import TaskGraph, TaskStep, TaskStatus
from app.intelligence.planning.task_store import task_store

logger = logging.getLogger("app.intelligence.planner")

class PlannerService:
    @staticmethod
    def create_plan(
        goal: str,
        domain: str = "general",
        user_id: str = "default_local_user"
    ) -> TaskGraph:
        """
        Synthesizes a structured multi-step TaskGraph for a user goal and persists it to SQLite/PostgreSQL.
        Supports sequential steps, parallel branches, conditional steps, and dependencies.
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        steps: List[TaskStep] = []

        goal_lower = goal.lower()
        subdomains: List[str] = []
        domain_transitions: List[Dict[str, Any]] = []
        approval_requirements: List[str] = []

        # 1. Multi-domain Archetype: Archaeology + History
        if any(k in goal_lower for k in ["archaeol", "excavation", "pottery"]) and any(k in goal_lower for k in ["histor", "record", "archive"]):
            subdomains = ["archaeology", "vision", "history", "research", "writing"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Analyze Excavation Photographs & Pottery Artifacts",
                    description="Inspects artifact features, typologies, and excavation stratigraphy.",
                    domain="archaeology",
                    tool_id="file.read",
                    arguments={"file_path": "excavation_photos.jpg"},
                    step_type="OBSERVATION",
                    risk_level="low",
                    approval_required=False
                ),
                TaskStep(
                    step_id="step_2",
                    title="Compare Findings with Historical Archival Records",
                    description="Receives pottery observation artifact as evidence and matches against historical records.",
                    domain="history",
                    dependencies=["step_1"],
                    tool_id="browser.search",
                    arguments={"query": "historical archival records settlement pottery"},
                    step_type="OBSERVATION",
                    risk_level="low",
                    approval_required=False
                ),
                TaskStep(
                    step_id="step_3",
                    title="Perform Multi-Source Research & Conflict Detection",
                    description="Decomposes research query across archaeology and history domains, synthesizing evidence.",
                    domain="research",
                    dependencies=["step_2"],
                    tool_id="browser.search",
                    arguments={"query": goal},
                    step_type="SYNTHESIS",
                    risk_level="medium",
                    approval_required=True,
                    approval_state="pending"
                ),
                TaskStep(
                    step_id="step_4",
                    title="Draft Comprehensive Archaeological & Historical Report",
                    description="Formulates evidence-backed research report preserving provenance and citation mappings.",
                    domain="writing",
                    dependencies=["step_3"],
                    tool_id="file.read",
                    arguments={"file_path": "final_settlement_report.md"},
                    step_type="ACTION",
                    risk_level="low",
                    approval_required=False
                )
            ]
            domain_transitions = [
                {"from": "archaeology", "to": "vision", "reason": "Visual feature extraction of pottery artifacts"},
                {"from": "vision", "to": "history", "reason": "Comparative archival analysis of artifact typology"},
                {"from": "history", "to": "research", "reason": "Evidence-backed cross-domain research synthesis"},
                {"from": "research", "to": "writing", "reason": "Final report compilation with provenance"}
            ]
            approval_requirements.append("step_3")

        # 2. Multi-domain Archetype: Cybersecurity + Career
        elif "cybersecurity" in goal_lower and not ("apply" in goal_lower) and ("career" in goal_lower or "engineer" in goal_lower or "job" in goal_lower):
            subdomains = ["cybersecurity", "cs", "software", "career", "education"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Security Knowledge & Skill Audit",
                    description="Audits current cybersecurity certifications, vulnerability skills, and theoretical CS background.",
                    domain="cybersecurity",
                    tool_id="file.search",
                    arguments={"query": "security audit skills"},
                    step_type="OBSERVATION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Computer Science & Systems Programming Roadmap",
                    description="Builds hands-on C++/Python systems programming & networking curriculum.",
                    domain="cs",
                    dependencies=["step_1"],
                    tool_id="code.execute",
                    arguments={"code": "# Systems programming exercise"},
                    step_type="ACTION",
                    risk_level="medium",
                    approval_required=True,
                    approval_state="pending"
                ),
                TaskStep(
                    step_id="step_3",
                    title="Career Mentorship & Resume Alignment",
                    description="Tailors Master Resume for Cybersecurity Engineering roles.",
                    domain="career",
                    dependencies=["step_2"],
                    tool_id="career.tailor_resume",
                    arguments={"jd_text": "Cybersecurity Engineer", "company": "Target Sec Firm", "role": "Security Engineer"},
                    step_type="ACTION",
                    risk_level="low"
                )
            ]
            domain_transitions = [
                {"from": "cybersecurity", "to": "cs", "reason": "Foundational systems knowledge roadmap"},
                {"from": "cs", "to": "career", "reason": "Targeted resume tailoring and market positioning"}
            ]
            approval_requirements.append("step_2")

        # 3. Compound Research, Report, Save, and Email Workflow (Prompt Section 2 Example)
        elif ("research" in goal_lower or "information" in goal_lower) and "report" in goal_lower and ("email" in goal_lower or "save" in goal_lower):
            subdomains = ["research", "writing", "workspace", "communication"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Gather Multi-Source Literature & Grounding Evidence",
                    description=f"Queries web and literature sources for '{goal}'.",
                    domain="research",
                    tool_id="browser.search",
                    arguments={"query": goal},
                    step_type="OBSERVATION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Compare Sources & Synthesize Fact-Checked Evidence",
                    description="Synthesizes findings into FACT, SOURCE-DERIVED, INFERENCE, and UNCERTAIN claims.",
                    domain="research",
                    dependencies=["step_1"],
                    tool_id="research.synthesize",
                    arguments={"topic": goal, "sources": ["Web Literature", "Grounding Documents"]},
                    step_type="SYNTHESIS",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_3",
                    title="Generate Structured Comprehensive Research Report",
                    description="Compiles structured markdown report with sections and citations.",
                    domain="writing",
                    dependencies=["step_2"],
                    tool_id="document.generate_report",
                    arguments={"title": f"Research Report: {goal[:40]}", "content": f"Executive analysis of {goal}"},
                    step_type="ACTION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_4",
                    title="Save & Organize Report in Project Workspace",
                    description="Saves and categorizes document in the user's project workspace.",
                    domain="workspace",
                    dependencies=["step_3"],
                    tool_id="file.write",
                    arguments={"file_path": "research_report.md", "content": f"# Research Report on {goal}\nVerified findings.\n"},
                    step_type="ACTION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_5",
                    title="Prepare Professional Email Draft",
                    description="Drafts a synthesized email summary for external stakeholders.",
                    domain="communication",
                    dependencies=["step_3"],
                    tool_id="email.draft",
                    arguments={"recipient": "stakeholder@example.com", "subject": f"Summary: {goal[:30]}", "body": f"Please find the executive research report summary on {goal}."},
                    step_type="ACTION",
                    risk_level="low"
                )
            ]
            domain_transitions = [
                {"from": "research", "to": "writing", "reason": "Drafting structured research report"},
                {"from": "writing", "to": "workspace", "reason": "Persisting artifact to workspace"},
                {"from": "writing", "to": "communication", "reason": "Preparing stakeholder email"}
            ]

        # 4. Computer Control & Multimodal Desktop Workflow
        elif any(k in goal_lower for k in ["desktop", "window", "screenshot", "active app", "screen"]):
            subdomains = ["desktop", "vision", "automation"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Observe Active Application & Desktop Context",
                    description="Inspects active window title, process ID, and accessibility bounds.",
                    domain="desktop",
                    tool_id="desktop.observe",
                    arguments={},
                    step_type="OBSERVATION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Capture High-Resolution Screen State",
                    description="Captures active window screenshot for multimodal analysis.",
                    domain="desktop",
                    dependencies=["step_1"],
                    tool_id="desktop.capture_screenshot",
                    arguments={"scope": "active_window"},
                    step_type="OBSERVATION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_3",
                    title="Multimodal OCR & Layout Understanding",
                    description="Processes visual UI layout and extracts text safely.",
                    domain="vision",
                    dependencies=["step_2"],
                    tool_id="multimodal.analyze_screenshot",
                    arguments={"image_path": "screenshot.png"},
                    step_type="OBSERVATION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_4",
                    title="Insert Formatted Response into Active Application",
                    description="Inserts synthesized text directly into the focused field (protected from credential managers).",
                    domain="desktop",
                    dependencies=["step_3"],
                    tool_id="desktop.insert_text",
                    arguments={"text": f"Analysis of active screen context for: {goal}", "target_app": "Editor"},
                    step_type="ACTION",
                    risk_level="medium"
                )
            ]

        # 5. File Operations & Directory Management Workflow
        elif ("file" in goal_lower or "folder" in goal_lower or "organize" in goal_lower) and any(k in goal_lower for k in ["organize", "move", "delete", "copy", "clean"]):
            subdomains = ["files", "workspace"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Inspect & Search Workspace Files",
                    description="Scans directory for files matching target criteria.",
                    domain="files",
                    tool_id="file.search",
                    arguments={"query": goal},
                    step_type="OBSERVATION",
                    risk_level="low"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Organize Directory by Categories",
                    description="Moves files into organized subfolders by extension and topic.",
                    domain="files",
                    dependencies=["step_1"],
                    tool_id="file.organize",
                    arguments={"directory": "workspace"},
                    step_type="ACTION",
                    risk_level="low"
                )
            ]
            if "delete" in goal_lower:
                steps.append(
                    TaskStep(
                        step_id="step_3",
                        title="Delete Obsolete File (Requires Human Approval)",
                        description="Permanently removes target obsolete file after confirmation.",
                        domain="files",
                        dependencies=["step_2"],
                        tool_id="file.delete",
                        arguments={"file_path": "workspace/obsolete_file.tmp"},
                        step_type="ACTION",
                        risk_level="high",
                        approval_required=True,
                        approval_state="pending"
                    )
                )
                approval_requirements.append("step_3")

        # 6. Career Tailoring & Interview Prep Workflow
        elif "apply" in goal_lower or "job" in goal_lower or "resume" in goal_lower or "c++" in goal_lower:
            subdomains = ["career", "writing"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Extract Job Description Requirements",
                    description="Parses hard skills and qualifications from the target job posting.",
                    domain="career",
                    tool_id="career.analyze_jd",
                    arguments={"jd_text": goal},
                    step_type="OBSERVATION"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Perform truthful Evidence Matching & Gap Analysis",
                    description="Matches Master Resume facts against extracted requirements and flags skill gaps.",
                    domain="career",
                    dependencies=["step_1"],
                    tool_id="career.tailor_resume",
                    arguments={"jd_text": goal, "company": "Target Company", "role": "Target Role"},
                    step_type="ACTION"
                ),
                TaskStep(
                    step_id="step_3",
                    title="Generate Targeted Interview Preparation Questions",
                    description="Formulates technical, behavioral, and gap-related interview questions.",
                    domain="career",
                    dependencies=["step_2"],
                    tool_id="career.prepare_interview",
                    arguments={"jd_text": goal, "company": "Target Company", "role": "Target Role"},
                    step_type="ACTION"
                )
            ]

        # 7. Deep Research & Academic Papers Workflow
        elif "research" in goal_lower or "paper" in goal_lower or "biology" in goal_lower:
            subdomains = [domain if domain != "general" else "research", "writing"]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Search Academic & Web Literature",
                    description="Queries grounding sources for literature matches.",
                    domain="research",
                    tool_id="browser.search",
                    arguments={"query": goal},
                    step_type="OBSERVATION"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Synthesize Multi-Source Findings",
                    description="Combines paper findings into structured research notes.",
                    domain="writing",
                    dependencies=["step_1"],
                    tool_id="file.read",
                    arguments={"file_path": "research_summary.txt"},
                    step_type="OBSERVATION"
                )
            ]

        # 8. Inspection & Workspace Summarization Workflow
        elif any(k in goal_lower for k in ["inspect", "summarize", "notes", "check"]):
            subdomains = [domain]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Search Workspace Files",
                    description=f"Inspects inputs and workspace files for '{goal}'.",
                    domain=domain,
                    tool_id="file.search",
                    arguments={"query": goal},
                    step_type="OBSERVATION"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Read & Summarize Findings",
                    description=f"Reads file content and formulates summary for '{goal}'.",
                    domain=domain,
                    dependencies=["step_1"],
                    tool_id="file.read",
                    arguments={"file_path": "summary_notes.txt"},
                    step_type="OBSERVATION"
                )
            ]

        # 9. General Purpose Autonomous Task Workflow
        else:
            subdomains = [domain]
            steps = [
                TaskStep(
                    step_id="step_1",
                    title="Analyze Task Context",
                    description=f"Inspects inputs and workspace files for '{goal}'.",
                    domain=domain,
                    tool_id="file.search",
                    arguments={"query": goal},
                    step_type="OBSERVATION"
                ),
                TaskStep(
                    step_id="step_2",
                    title="Execute Core Objective",
                    description=f"Performs core action for '{goal}'.",
                    domain=domain,
                    dependencies=["step_1"],
                    tool_id="code.execute",
                    arguments={"code": f"# Execution script for {goal}\nprint('Task completed.')"},
                    step_type="ACTION"
                )
            ]

        graph = TaskGraph(
            task_id=task_id,
            user_id=user_id,
            goal=goal,
            domain=domain,
            subdomains=subdomains,
            steps=steps,
            domain_transitions=domain_transitions,
            approval_requirements=approval_requirements
        )

        # Persist to Task Store
        task_store.save_task(
            task_id=task_id,
            objective=goal,
            domain=domain,
            status=graph.status.value,
            user_id=user_id,
            steps=[s.model_dump() for s in steps],
            metadata={
                "checkpoints": graph.checkpoints,
                "replan_count": graph.replan_count,
                "subdomains": subdomains
            }
        )

        return graph

    @staticmethod
    def replan_on_failure(
        task_id: str,
        failed_step_id: str,
        error_message: str,
        failure_diagnosis: Optional[str] = None
    ) -> Optional[TaskGraph]:
        """
        Dynamic re-planning upon step failure or verification failure.
        Diagnoses failure, prevents infinite loops, and injects safe recovery step.
        """
        task_data = task_store.get_task(task_id)
        if not task_data:
            return None

        steps_raw = task_data.get("steps", [])
        metadata = task_data.get("metadata", {})
        replan_count = metadata.get("replan_count", 0)

        # Loop guard: max 3 replans per task
        if replan_count >= 3:
            logger.warning(f"Task '{task_id}' exceeded max replan limit (3). Halting execution to prevent infinite loop.")
            task_store.update_task_status(task_id=task_id, status="failed")
            return None

        replan_count += 1
        metadata["replan_count"] = replan_count

        # Diagnose failure and choose appropriate fallback tool
        fallback_tool = "file.read"
        fallback_args: Dict[str, Any] = {"file_path": "error_recovery.log"}
        fallback_title = f"Corrective Recovery for {failed_step_id}"

        if "browser" in error_message.lower():
            fallback_tool = "browser.search"
            fallback_args = {"query": f"fallback alternative for {failed_step_id}"}
            fallback_title = f"Web Search Fallback for {failed_step_id}"
        elif "file" in error_message.lower() or "exist" in error_message.lower():
            fallback_tool = "file.write"
            fallback_args = {"file_path": "recovery_output.txt", "content": f"# Recovered State\nAuto-generated after {failed_step_id} issue: {error_message}\n"}
            fallback_title = f"Workspace State Recovery for {failed_step_id}"
        elif "desktop" in error_message.lower():
            fallback_tool = "desktop.observe"
            fallback_args = {}
            fallback_title = f"Desktop State Re-observation for {failed_step_id}"

        fallback_step = {
            "step_id": f"step_fallback_{len(steps_raw) + 1}",
            "title": fallback_title,
            "description": f"Fallback step generated after failure: {error_message}. Diagnosis: {failure_diagnosis or 'Step outcome unverified'}",
            "status": "pending",
            "dependencies": [failed_step_id],
            "tool_id": fallback_tool,
            "arguments": fallback_args,
            "step_type": "ACTION",
            "risk_level": "low",
            "approval_required": False,
            "approval_state": "not_required",
            "result": None,
            "error": None
        }
        steps_raw.append(fallback_step)

        task_store.update_task_status(task_id=task_id, status="in_progress", steps=steps_raw)
        task_store.update_task_metadata(task_id=task_id, metadata=metadata)

        res = task_store.get_task(task_id)
        return TaskGraph(
            task_id=res["task_id"],
            user_id=res["user_id"],
            goal=res["objective"],
            domain=res["domain"],
            status=TaskStatus(res["status"]),
            steps=[TaskStep(**s) for s in res["steps"]],
            replan_count=replan_count
        )

    @staticmethod
    def cancel_task(task_id: str) -> bool:
        res = task_store.update_task_status(task_id=task_id, status="cancelled")
        return res is not None

    @staticmethod
    def pause_task(task_id: str) -> Optional[Dict[str, Any]]:
        return task_store.update_task_status(task_id=task_id, status="paused")

    @staticmethod
    def resume_task(task_id: str) -> Optional[Dict[str, Any]]:
        return task_store.update_task_status(task_id=task_id, status="in_progress")

    @staticmethod
    def create_checkpoint(task_id: str, checkpoint_name: str) -> Optional[str]:
        task_data = task_store.get_task(task_id)
        if not task_data:
            return None
        chk_id = f"chk_{uuid.uuid4().hex[:8]}"
        snapshot = {
            "checkpoint_id": chk_id,
            "name": checkpoint_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "steps": task_data.get("steps", []),
            "status": task_data.get("status")
        }
        task_store.save_checkpoint(task_id, chk_id, snapshot)
        return chk_id

    @staticmethod
    def rollback_to_checkpoint(task_id: str, checkpoint_id: str) -> Optional[TaskGraph]:
        checkpoints = task_store.get_checkpoints(task_id)
        if checkpoint_id not in checkpoints:
            return None
        snapshot = checkpoints[checkpoint_id]
        steps = snapshot.get("steps", [])
        task_store.update_task_status(task_id=task_id, status="in_progress", steps=steps)
        res = task_store.get_task(task_id)
        return TaskGraph(
            task_id=res["task_id"],
            user_id=res["user_id"],
            goal=res["objective"],
            domain=res["domain"],
            status=TaskStatus(res["status"]),
            steps=[TaskStep(**s) for s in res["steps"]]
        )

planner_service = PlannerService()
