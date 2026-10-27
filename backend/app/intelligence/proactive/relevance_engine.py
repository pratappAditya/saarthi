"""
Relevance & Anti-Fatigue Engine (Phase 8 - Proactive Saarthi 2.0).
Evaluates whether a proactive suggestion is justified based on relevance,
urgency, actionability, user preferences, quiet hours, cooldowns, and dismissal fatigue.
Answers: 'Why should Saarthi surface this now?'
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, time

from app.intelligence.proactive.proactive_models import (
    ProactiveEvent, ProactiveSuggestion, UserProactiveSettings,
    ProactiveEventCategory, ProactivePriority
)

logger = logging.getLogger("app.intelligence.relevance_engine")


class RelevanceEngine:
    def __init__(self):
        # In-memory record of recent suggestions per user: user_id -> List[(fingerprint, timestamp)]
        self._history: Dict[str, List[Tuple[str, datetime]]] = {}

    def is_quiet_hours(self, settings: UserProactiveSettings, current_dt: Optional[datetime] = None) -> bool:
        """
        Determines if current time falls within user-configured quiet hours.
        """
        if not settings.quiet_hours_enabled:
            return False

        dt = current_dt or datetime.now()
        cur_time = dt.time()

        try:
            sh, sm = map(int, settings.quiet_hours_start.split(":"))
            eh, em = map(int, settings.quiet_hours_end.split(":"))
            start_t = time(sh, sm)
            end_t = time(eh, em)

            if start_t <= end_t:
                return start_t <= cur_time <= end_t
            else:
                # Overnight quiet hours, e.g. 22:00 to 08:00
                return cur_time >= start_t or cur_time <= end_t
        except Exception as e:
            logger.warning(f"Error parsing quiet hours '{settings.quiet_hours_start}-{settings.quiet_hours_end}': {e}")
            return False

    def evaluate_justification(
        self,
        event: ProactiveEvent,
        settings: UserProactiveSettings,
        current_dt: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines if a proactive interruption is justified for the user.
        Returns (is_justified, suppression_reason).
        """
        now = current_dt or datetime.now(timezone.utc)

        # 1. Global Proactivity Enabled
        if not settings.enabled:
            return False, "Proactive assistance is disabled by user setting."

        # 2. Category Level Disabled
        cat_key = event.category.value
        if not settings.enabled_categories.get(cat_key, True):
            return False, f"Category '{cat_key}' is disabled by user preference."

        # 3. Explicitly Disabled Type
        if cat_key in settings.disabled_types or event.source in settings.disabled_types:
            return False, f"Type '{cat_key}' is explicitly silenced."

        # 4. Quiet Hours Check (Critical and Security bypass quiet hours)
        is_critical = (
            event.category in [ProactiveEventCategory.SECURITY_EVENT, ProactiveEventCategory.AGENT_FAILURE]
            or event.importance >= 0.95
        )
        if not is_critical and self.is_quiet_hours(settings, current_dt=now):
            return False, "Suppressed: Currently within user-configured quiet hours."

        # 5. Dismissal Fatigue / Repeated Dismissal Suppression
        fingerprint = f"{event.category.value}:{event.data.get('topic', event.source)}"
        dismissal_count = settings.dismissal_counts.get(fingerprint, 0)
        if dismissal_count >= 3:
            return False, f"Suppressed: User dismissed '{fingerprint}' {dismissal_count} times (anti-fatigue threshold met)."

        # 6. Cooldown / Deduplication
        user_history = self._history.setdefault(event.user_id, [])
        cutoff_seconds = settings.cooldown_minutes * 60
        for fp, ts in user_history:
            if fp == fingerprint:
                elapsed = (now - ts).total_seconds() if ts.tzinfo else (datetime.now() - ts).total_seconds()
                if elapsed < cutoff_seconds:
                    return False, f"Suppressed: In cooldown period ({int(cutoff_seconds - elapsed)}s remaining)."

        # 7. Actionability & Confidence Thresholds
        if not event.actionability:
            return False, "Suppressed: Event contains no actionable recommendation or user decision."
        if event.confidence < 0.60:
            return False, f"Suppressed: Low confidence ({event.confidence:.2f} < 0.60)."

        return True, None

    def record_shown(self, user_id: str, suggestion: ProactiveSuggestion, now: Optional[datetime] = None) -> None:
        """
        Records that a suggestion was surfaced for cooldown tracking.
        """
        ts = now or datetime.now(timezone.utc)
        fingerprint = f"{suggestion.type.value}:{suggestion.arguments.get('topic', suggestion.title)}"
        user_history = self._history.setdefault(user_id, [])
        user_history.append((fingerprint, ts))
        # Keep only last 50
        if len(user_history) > 50:
            self._history[user_id] = user_history[-50:]

    def build_rationale(self, event: ProactiveEvent) -> str:
        """
        Synthesizes an explainable, non-manipulative rationale ('Because...').
        """
        cat = event.category
        d = event.data

        if cat == ProactiveEventCategory.GOAL_PROGRESS:
            return f"Because goal '{d.get('goal_title', 'active goal')}' has {d.get('remaining_count', 'unresolved')} remaining milestones and target date is {d.get('target_date', 'approaching')}."
        elif cat == ProactiveEventCategory.DEADLINE_APPROACHING:
            return f"Because deadline for '{d.get('item_title', 'task')}' is approaching in {d.get('time_left', 'less than 24 hours')}."
        elif cat == ProactiveEventCategory.AGENT_FAILURE:
            return f"Because your agent task stopped at step '{d.get('failed_step', 'execution')}' with error: '{d.get('error', 'verification failed')}'."
        elif cat == ProactiveEventCategory.AGENT_APPROVAL_NEEDED:
            return f"Because an agent requires explicit server-side authorization for high-risk tool '{d.get('tool_id', 'action')}'."
        elif cat == ProactiveEventCategory.AGENT_COMPLETION:
            return f"Because agent task '{d.get('task_name', 'workflow')}' completed with verified deliverables on disk."
        elif cat == ProactiveEventCategory.RESEARCH_CHANGE:
            return f"Because conflicting evidence or superseded standards were detected regarding '{d.get('topic', 'your research')}'."
        elif cat == ProactiveEventCategory.ROUTINE_DUE:
            return f"Because scheduled routine '{d.get('routine_name', 'routine')}' is due for execution per your configuration."
        elif cat == ProactiveEventCategory.WORKFLOW_PATTERN:
            return f"Because you performed this sequence ({d.get('pattern_name', 'workflow')}) multiple times this week; Saarthi can automate it upon approval."
        elif cat == ProactiveEventCategory.DOCUMENT_CHANGE:
            return f"Because project file '{d.get('filename', 'document')}' was updated with new sections."
        elif cat == ProactiveEventCategory.TASK_BLOCKED:
            return f"Because task '{d.get('task_title', 'step')}' is waiting on dependency '{d.get('dependency', 'previous milestone')}'."
        else:
            return f"Because an event in your active workspace requires attention: {event.source}."


relevance_engine = RelevanceEngine()
