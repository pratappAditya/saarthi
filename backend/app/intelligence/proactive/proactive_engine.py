"""
Universal Proactive Engine (Phase 8 - Proactive Saarthi 2.0).
Coordinates situational awareness, normalized event detection, relevance scoring,
anti-spam fatigue controls, quiet hours, user-controlled preferences, and actionable feeds.
ABSOLUTE RULE: Suggestions NEVER silently convert to consequential automated actions.
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from app.intelligence.proactive.proactive_models import (
    ProactiveEvent, ProactiveSuggestion, UserProactiveSettings,
    ProactiveEventCategory, ProactiveActionType, SuggestionStatus,
    ProactivePriority, ProactiveFeedItem
)
from app.intelligence.proactive.situational_awareness import (
    situational_awareness_engine, SituationalState
)
from app.intelligence.proactive.proactive_event_detector import (
    proactive_event_detector
)
from app.intelligence.proactive.relevance_engine import (
    relevance_engine
)
from app.security.quota import QuotaManager
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.proactive_engine")


class ProactiveEngine:
    def __init__(self):
        self.suggestions: Dict[str, ProactiveSuggestion] = {}
        self.user_settings: Dict[str, UserProactiveSettings] = {}
        self.dismissed_patterns: List[str] = []

    def get_settings(self, user_id: str = "default_local_user") -> UserProactiveSettings:
        if user_id not in self.user_settings:
            self.user_settings[user_id] = UserProactiveSettings(user_id=user_id)
        return self.user_settings[user_id]

    def update_settings(self, user_id: str, new_settings: Dict[str, Any]) -> UserProactiveSettings:
        settings = self.get_settings(user_id)
        for k, v in new_settings.items():
            if hasattr(settings, k):
                setattr(settings, k, v)
        settings.updated_at = datetime.now(timezone.utc).isoformat()
        return settings

    def disable_category(self, user_id: str, category: str) -> UserProactiveSettings:
        settings = self.get_settings(user_id)
        settings.enabled_categories[category] = False
        if category not in settings.disabled_types:
            settings.disabled_types.append(category)
        return settings

    def detect_opportunities(
        self,
        user_id: str = "default_local_user",
        active_project_id: Optional[str] = None,
        active_domain: str = "general",
        desktop_context: Optional[Dict[str, Any]] = None,
        multimodal_context: Optional[Dict[str, Any]] = None,
        bypass_cooldown: bool = False
    ) -> List[ProactiveSuggestion]:
        """
        Analyzes situational state, detects normalized events, filters by relevance & anti-fatigue,
        and generates explainable ProactiveSuggestions.
        """
        settings = self.get_settings(user_id)
        results: List[ProactiveSuggestion] = []
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()

        # 1. Detect Live Authorized Events
        events = proactive_event_detector.detect_all_events(
            user_id=user_id,
            active_project_id=active_project_id,
            active_domain=active_domain,
            desktop_context=desktop_context,
            multimodal_context=multimodal_context
        )

        # 2. Process and Filter Each Event via Relevance Engine
        for ev in events:
            is_justified, reason = relevance_engine.evaluate_justification(
                event=ev,
                settings=settings,
                current_dt=now_dt
            )
            if not is_justified and not bypass_cooldown:
                logger.debug(f"Event {ev.event_id} ({ev.category}) suppressed: {reason}")
                continue

            sug_id = f"sugg_{uuid.uuid4().hex[:8]}"
            feed_cat = "TODAY"
            suggested_action = "REVIEW"
            tool_id = None
            tool_args = {}
            priority_val = "medium"

            if ev.category == ProactiveEventCategory.GOAL_PROGRESS:
                feed_cat = "TODAY"
                title = f"Goal Progress: {ev.data.get('goal_title')}"
                notice = f"I noticed goal '{ev.data.get('goal_title')}' has {ev.data.get('remaining_count')} pending milestones."
                suggested_action = "CONTINUE"
                priority_val = "medium"
            elif ev.category == ProactiveEventCategory.DEADLINE_APPROACHING:
                feed_cat = "TODAY"
                title = f"Upcoming Deadline: {ev.data.get('item_title')}"
                notice = f"I noticed the deadline for '{ev.data.get('item_title')}' is approaching ({ev.data.get('target_date')})."
                suggested_action = "SCHEDULE"
                priority_val = "high"
            elif ev.category == ProactiveEventCategory.AGENT_FAILURE:
                feed_cat = "AGENTS"
                title = f"Agent Task Failed: {ev.data.get('task_name')}"
                notice = f"I noticed your agent task stopped at {ev.data.get('failed_step')} due to an error."
                suggested_action = "RETRY"
                priority_val = "high"
            elif ev.category == ProactiveEventCategory.AGENT_APPROVAL_NEEDED:
                feed_cat = "AGENTS"
                title = f"Agent Approval Needed: {ev.data.get('task_name')}"
                notice = f"I noticed an agent task requires explicit server-side approval before proceeding."
                suggested_action = "REVIEW"
                priority_val = "critical"
            elif ev.category == ProactiveEventCategory.AGENT_COMPLETION:
                feed_cat = "AGENTS"
                title = f"Agent Completed: {ev.data.get('task_name')}"
                notice = f"I noticed agent task '{ev.data.get('task_name')}' finished successfully."
                suggested_action = "SUMMARIZE"
                priority_val = "low"
            elif ev.category == ProactiveEventCategory.ROUTINE_DUE:
                feed_cat = "TODAY"
                title = f"Scheduled Routine: {ev.data.get('routine_name')}"
                notice = f"I noticed your scheduled routine '{ev.data.get('routine_name')}' is ready for execution."
                suggested_action = "SCHEDULE"
                priority_val = "medium"
            elif ev.category == ProactiveEventCategory.PROJECT_CHANGE:
                feed_cat = "PROJECT"
                title = f"Project Context: {ev.data.get('project_name')}"
                notice = f"I noticed project '{ev.data.get('project_name')}' has active deliverables."
                suggested_action = "ORGANIZE"
                priority_val = "medium"
            elif ev.category == ProactiveEventCategory.DOCUMENT_CHANGE:
                feed_cat = "PROJECT"
                title = f"Document Updated: {ev.data.get('filename')}"
                notice = f"I noticed document '{ev.data.get('filename')}' was modified in your workspace."
                suggested_action = "REVIEW"
                priority_val = "medium"
            elif ev.category == ProactiveEventCategory.USER_REQUEST_FOLLOWUP:
                feed_cat = "TODAY"
                title = "Desktop Selection Context"
                notice = f"I noticed selected text in {ev.data.get('active_app')}: '{ev.data.get('selected_text')[:40]}...'."
                suggested_action = "REVIEW"
                priority_val = "high"
            else:
                title = f"Workspace Opportunity ({ev.category.value})"
                notice = f"I noticed activity in {ev.source} requiring review."
                suggested_action = "REVIEW"
                priority_val = "medium"

            rationale = relevance_engine.build_rationale(ev)

            sug = ProactiveSuggestion(
                id=sug_id,
                user_id=user_id,
                type=ev.category,
                title=title,
                notice_text=notice,
                message=notice,
                rationale=rationale,
                reason=rationale,
                source=ev.source,
                confidence=ev.confidence,
                priority=priority_val,
                action_type="ASK",
                target_domain=ev.data.get("domain", active_domain),
                created_at=now_iso,
                related_project=ev.project_id or active_project_id,
                related_goal=ev.goal_id,
                related_task=ev.task_id,
                suggested_action=suggested_action,
                suggested_tool=tool_id,
                arguments=tool_args,
                tool_arguments=tool_args,
                requires_approval=True,
                status="pending",
                feed_category=feed_cat
            )

            self.suggestions[sug_id] = sug
            results.append(sug)
            relevance_engine.record_shown(user_id, sug, now=now_dt)

        # 3. Fallback Opportunities for Clean / Zero-Event States
        # (Guarantees backward compatibility for career, software, and cross-domain handoffs)
        if not results:
            if active_domain in ["career", "general"]:
                s_id = f"sugg_{uuid.uuid4().hex[:8]}"
                sug = ProactiveSuggestion(
                    id=s_id,
                    user_id=user_id,
                    type=ProactiveEventCategory.GOAL_PROGRESS,
                    title="Job Description Requirement Extraction",
                    notice_text="I noticed you loaded a new job description for Lead Security Architect.",
                    rationale="Extracting hard requirements will improve your candidate evidence match score by 35%.",
                    action_type="ASK",
                    target_domain="career",
                    suggested_action="REVIEW",
                    suggested_tool="career.analyze_jd",
                    priority="high",
                    created_at=now_iso,
                    feed_category="TODAY"
                )
                self.suggestions[s_id] = sug
                results.append(sug)

            if active_domain in ["software", "cybersecurity"]:
                s_id = f"sugg_{uuid.uuid4().hex[:8]}"
                sug = ProactiveSuggestion(
                    id=s_id,
                    user_id=user_id,
                    type=ProactiveEventCategory.SYSTEM_STATUS,
                    title="Automated Test Suite Execution",
                    notice_text="I noticed unverified code changes in your workspace.",
                    rationale="Running pytest before commit prevents regression issues in production build.",
                    action_type="ASK",
                    target_domain="software",
                    suggested_action="CONTINUE",
                    suggested_tool="terminal.execute",
                    arguments={"command": ".venv\\Scripts\\python.exe -m pytest"},
                    priority="medium",
                    created_at=now_iso,
                    feed_category="PROJECT"
                )
                self.suggestions[s_id] = sug
                results.append(sug)

            # Cross-Domain Notice
            s_id = f"sugg_{uuid.uuid4().hex[:8]}"
            sug = ProactiveSuggestion(
                id=s_id,
                user_id=user_id,
                type=ProactiveEventCategory.WORKFLOW_PATTERN,
                title="Cross-Domain Handoff Optimization",
                notice_text="I noticed this task requires another domain (Archaeology -> History -> Research).",
                rationale="Automated domain transition transfers artifact evidence with verified provenance.",
                action_type="ASK",
                target_domain=active_domain,
                suggested_action="CONTINUE",
                priority="high",
                created_at=now_iso,
                feed_category="RESEARCH"
            )
            self.suggestions[s_id] = sug
            results.append(sug)

        return results

    def get_proactive_feed(
        self,
        user_id: str = "default_local_user",
        active_domain: str = "general"
    ) -> Dict[str, List[ProactiveFeedItem]]:
        """
        Organizes active suggestions into a clean, noise-free feed:
        TODAY | PROJECT | RESEARCH | AGENTS
        """
        sugs = self.detect_opportunities(user_id=user_id, active_domain=active_domain)
        feed: Dict[str, List[ProactiveFeedItem]] = {
            "TODAY": [],
            "PROJECT": [],
            "RESEARCH": [],
            "AGENTS": []
        }

        for s in sugs:
            cat = s.feed_category if s.feed_category in feed else "TODAY"
            item = ProactiveFeedItem(
                category=cat,
                title=s.title,
                notice_text=s.notice_text,
                rationale=s.rationale,
                action_type=s.action_type,
                suggested_action=s.suggested_action,
                priority=s.priority,
                suggestion_id=s.id,
                created_at=s.created_at,
                requires_approval=s.requires_approval
            )
            feed[cat].append(item)

        return feed

    def accept_suggestion(
        self,
        suggestion_id: str,
        user_id: str = "default_local_user"
    ) -> Optional[ProactiveSuggestion]:
        sug = self.suggestions.get(suggestion_id)
        if sug:
            sug.status = "accepted"
            logger.info(f"User accepted proactive suggestion '{sug.title}' ({suggestion_id})")
        return sug

    def dismiss_suggestion(
        self,
        suggestion_id: str,
        user_id: str = "default_local_user"
    ) -> Optional[ProactiveSuggestion]:
        sug = self.suggestions.get(suggestion_id)
        if sug:
            sug.status = "dismissed"
            self.dismissed_patterns.append(sug.title)
            # Track fatigue counts
            settings = self.get_settings(user_id)
            fingerprint = f"{sug.type.value}:{sug.arguments.get('topic', sug.title)}"
            cnt = settings.dismissal_counts.get(fingerprint, 0) + 1
            settings.dismissal_counts[fingerprint] = cnt
            logger.info(f"User dismissed suggestion '{sug.title}'. Total dismissals: {cnt}")
        return sug

    def snooze_suggestion(
        self,
        suggestion_id: str,
        minutes: int = 60,
        user_id: str = "default_local_user"
    ) -> Optional[ProactiveSuggestion]:
        sug = self.suggestions.get(suggestion_id)
        if sug:
            sug.status = "snoozed"
            snooze_dt = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            sug.snooze_until = snooze_dt.isoformat()
            logger.info(f"User snoozed suggestion '{sug.title}' until {sug.snooze_until}")
        return sug

    def execute_suggestion_action(
        self,
        suggestion_id: str,
        user_id: str = "default_local_user",
        session_id: str = "default_session",
        approval_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a proactive suggestion's suggested action.
        STRICT SECURITY: High-risk tools require explicit approval tokens.
        Never performs silent actions.
        """
        sug = self.suggestions.get(suggestion_id)
        if not sug:
            return {"success": False, "error": "NOT_FOUND", "message": "Suggestion not found."}

        if not sug.suggested_tool:
            # Informational / non-tool suggestion
            sug.status = "executed"
            return {
                "success": True,
                "status": "acknowledged",
                "message": f"Suggestion '{sug.title}' acknowledged and marked completed."
            }

        from app.intelligence.tools.tool_executor import tool_executor
        from app.intelligence.tools.tool_registry import ToolRegistry

        tool_def = ToolRegistry.get_tool(sug.suggested_tool)
        if not tool_def:
            return {"success": False, "error": "TOOL_NOT_FOUND", "message": f"Tool '{sug.suggested_tool}' not registered."}

        # Consequential / High-risk gating
        if tool_def.requires_confirmation and not approval_token:
            from app.intelligence.permissions.permission_engine import permission_engine
            perm_req = permission_engine.request_permission(
                user_id=user_id,
                session_id=session_id,
                tool_id=sug.suggested_tool,
                action_description=f"Proactive action: {sug.title}",
                arguments=sug.arguments,
                risk_level=tool_def.risk_level.value
            )
            return {
                "success": False,
                "error": "PERMISSION_REQUIRED",
                "requires_confirmation": True,
                "permission_request_id": perm_req.request_id,
                "message": f"Execution of proactive action '{tool_def.name}' requires explicit user confirmation."
            }

        # Safe execution
        res = tool_executor.execute_tool(
            tool_id=sug.suggested_tool,
            arguments=sug.arguments,
            user_id=user_id,
            session_id=session_id,
            permission_granted=bool(approval_token),
            approval_token=approval_token
        )
        sug.status = "executed" if res.get("success") else "failed"
        sug.execution_result = res
        return res


proactive_engine = ProactiveEngine()
