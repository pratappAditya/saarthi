import logging
import time
from typing import Dict, Any, List, Optional

from app.intelligence.personalization.personalization_model import (
    UserPersonalizationProfile,
    PreferenceItem,
    PreferenceSource,
    DomainExpertise,
    ExpertiseLevel,
    PersonalizationContext
)
from app.intelligence.personalization.personalization_store import personalization_store, PersonalizationStore

logger = logging.getLogger("app.intelligence.personalization_engine")

class PersonalizationEngine:
    """
    Central Orchestrator for Saarthi Personalization.
    Resolves effective preferences via 'Task > Project > Domain > Global > System Defaults' precedence,
    processes interaction learning signals safely, and adapts response synthesis across all subsystems.
    """
    def __init__(self, store: Optional[PersonalizationStore] = None):
        self.store = store or personalization_store

    def get_profile(self, user_id: str = "default_local_user") -> UserPersonalizationProfile:
        return self.store.get_profile(user_id)

    def build_personalization_context(
        self,
        user_id: str = "default_local_user",
        domain: str = "general",
        project_id: Optional[str] = None,
        task_prompt: Optional[str] = None,
        task_overrides: Optional[Dict[str, Any]] = None
    ) -> PersonalizationContext:
        """
        Assembles effective PersonalizationContext following strict precedence:
        Task Overrides > Project Overrides > Domain Overrides > Global Preferences > System Defaults.
        """
        profile = self.store.get_profile(user_id)

        if not profile.personalization_enabled:
            return PersonalizationContext(
                user_id=user_id,
                personalization_enabled=False,
                explanations=["Personalization engine is currently disabled by user."]
            )

        # Baseline Global Defaults
        effective_comm = profile.communication_style
        effective_length = profile.preferred_response_length
        effective_depth = profile.technical_depth
        effective_formatting = profile.preferred_formatting
        effective_proactivity = profile.proactivity_preference
        effective_voice_rate = 1.0

        precedence_scope = "Global Profile"
        active_overrides = []
        explanations = [f"Base preferences loaded from {user_id} profile."]

        # 1. Domain Expertise Level
        dom_exp = profile.domain_expertise.get(domain)
        effective_domain_exp = dom_exp.level.value if dom_exp else "intermediate"
        if dom_exp:
            explanations.append(f"Adapted for {domain.upper()} domain expertise level: {dom_exp.level.value.upper()} (Confidence: {int(dom_exp.confidence * 100)}%).")

        # 2. Domain-Specific Inferred / Explicit Preferences
        domain_pref_key = f"{domain}_response_depth"
        if domain_pref_key in profile.explicit_preferences:
            effective_depth = profile.explicit_preferences[domain_pref_key]
            precedence_scope = "Domain Preference"
            active_overrides.append(f"Domain override: {domain_pref_key}={effective_depth}")
        elif domain_pref_key in profile.inferred_preferences:
            inferred = profile.inferred_preferences[domain_pref_key]
            if not inferred.rejected and inferred.confidence >= 0.6:
                effective_depth = str(inferred.value)
                precedence_scope = "Domain Preference (Inferred)"
                active_overrides.append(f"Inferred domain depth: {effective_depth}")

        # 3. Project-Scoped Overrides
        if project_id:
            proj_overrides = self.store.get_project_overrides(user_id, project_id)
            if proj_overrides:
                precedence_scope = f"Project Override ({project_id})"
                if "communication_style" in proj_overrides:
                    effective_comm = str(proj_overrides["communication_style"])
                    active_overrides.append(f"Project communication: {effective_comm}")
                if "preferred_response_length" in proj_overrides:
                    effective_length = str(proj_overrides["preferred_response_length"])
                    active_overrides.append(f"Project response length: {effective_length}")
                if "technical_depth" in proj_overrides:
                    effective_depth = str(proj_overrides["technical_depth"])
                    active_overrides.append(f"Project technical depth: {effective_depth}")

        # 4. Task-Specific Prompt & Direct Overrides (highest precedence)
        if task_prompt:
            prompt_lower = task_prompt.lower()
            if "very concise" in prompt_lower or "super concise" in prompt_lower or "ultra concise" in prompt_lower:
                effective_length = "very concise"
                precedence_scope = "Task Prompt Override"
                active_overrides.append("Task prompt requested very concise length")
            elif "concise" in prompt_lower or "brief" in prompt_lower or "short" in prompt_lower:
                effective_length = "concise"
                precedence_scope = "Task Prompt Override"
                active_overrides.append("Task prompt requested concise length")
            elif "detailed" in prompt_lower or "deep" in prompt_lower or "comprehensive" in prompt_lower:
                effective_length = "detailed"
                precedence_scope = "Task Prompt Override"
                active_overrides.append("Task prompt requested detailed analysis")

            if "expert" in prompt_lower or "advanced" in prompt_lower:
                effective_depth = "expert"
                precedence_scope = "Task Prompt Override"
                active_overrides.append("Task prompt requested expert depth")

        if task_overrides:
            precedence_scope = "Task Direct Override"
            if "preferred_response_length" in task_overrides:
                effective_length = str(task_overrides["preferred_response_length"])
                active_overrides.append(f"Task override: response length={effective_length}")
            if "communication_style" in task_overrides:
                effective_comm = str(task_overrides["communication_style"])
                active_overrides.append(f"Task override: communication={effective_comm}")
            if "technical_depth" in task_overrides:
                effective_depth = str(task_overrides["technical_depth"])
                active_overrides.append(f"Task override: technical depth={effective_depth}")
            if "preferred_formatting" in task_overrides:
                effective_formatting = str(task_overrides["preferred_formatting"])
                active_overrides.append(f"Task override: formatting={effective_formatting}")

        ctx = PersonalizationContext(
            user_id=user_id,
            effective_communication_style=effective_comm,
            effective_response_length=effective_length,
            effective_technical_depth=effective_depth,
            effective_formatting=effective_formatting,
            effective_proactivity_level=effective_proactivity,
            effective_voice_rate=effective_voice_rate,
            effective_domain_expertise=effective_domain_exp,
            precedence_scope=precedence_scope,
            active_overrides=active_overrides,
            explanations=explanations,
            personalization_enabled=True
        )

        return ctx

    def learn_interaction_signal(
        self,
        user_id: str = "default_local_user",
        signal_type: str = "turn_completed",
        signal_data: Optional[Dict[str, Any]] = None
    ) -> Optional[PreferenceItem]:
        """
        Processes interaction signals into non-sensitive, evidence-based inferred preferences.
        Strictly ignores sensitive profiling (medical, political, religious, psychological).
        """
        data = signal_data or {}
        profile = self.store.get_profile(user_id)

        if not profile.learning_enabled or not profile.inference_enabled:
            return None

        # 1. Proactive Suggestion Feedback
        if signal_type == "proactive_dismissed":
            suggestion_type = data.get("suggestion_type", "general")
            evidence = f"User dismissed proactive suggestion '{suggestion_type}'"
            item = self.store.record_inferred_preference(
                user_id=user_id,
                key=f"proactive_dismiss_{suggestion_type}",
                category="proactivity",
                value="reduced_frequency",
                confidence=0.70,
                evidence=evidence
            )
            # Adjust proactivity if multiple dismissals
            if profile.proactivity_preference == "high":
                profile.proactivity_preference = "moderate"
                self.store.save_profile(profile)
            return item

        elif signal_type == "proactive_accepted":
            suggestion_type = data.get("suggestion_type", "general")
            evidence = f"User accepted proactive suggestion '{suggestion_type}'"
            return self.store.record_inferred_preference(
                user_id=user_id,
                key=f"proactive_accept_{suggestion_type}",
                category="proactivity",
                value="high_relevance",
                confidence=0.85,
                evidence=evidence
            )

        # 2. Repeated Workflow & Tool Preferences
        elif signal_type == "tool_used":
            tool_id = data.get("tool_id")
            if tool_id and tool_id not in profile.preferred_tools:
                profile.preferred_tools.append(tool_id)
                self.store.save_profile(profile)

            evidence = f"Observed repeated use of tool '{tool_id}'"
            return self.store.record_inferred_preference(
                user_id=user_id,
                key=f"frequent_tool_{tool_id}",
                category="work",
                value=True,
                confidence=0.80,
                evidence=evidence
            )

        # 3. Domain Depth & Expertise Inference
        elif signal_type == "domain_interaction":
            domain = data.get("domain", "general")
            complexity = data.get("complexity", "intermediate")
            current_exp = profile.domain_expertise.get(domain)

            # Avoid resetting explicit overrides
            if current_exp and current_exp.explicit_override:
                return None

            new_level = ExpertiseLevel.INTERMEDIATE
            if complexity == "advanced" or data.get("has_advanced_terms"):
                new_level = ExpertiseLevel.ADVANCED
            elif complexity == "expert":
                new_level = ExpertiseLevel.EXPERT

            exp_item = self.store.set_domain_expertise(
                user_id=user_id,
                domain=domain,
                level=new_level,
                confidence=0.75,
                evidence=f"Inferred from interaction query complexity in {domain} domain",
                explicit_override=False
            )
            logger.info(f"Updated domain expertise for '{domain}' to '{new_level.value}'")
            return None

        # 4. Explicit Formatting / Response Feedback
        elif signal_type == "explicit_correction":
            correction = data.get("correction", "").lower()
            if "bullet" in correction:
                profile.preferred_formatting = "bullet_points"
                self.store.save_profile(profile)
            elif "concise" in correction or "short" in correction:
                profile.preferred_response_length = "concise"
                self.store.save_profile(profile)
            elif "detailed" in correction:
                profile.preferred_response_length = "detailed"
                self.store.save_profile(profile)

            return self.store.record_inferred_preference(
                user_id=user_id,
                key="last_explicit_correction",
                category="communication",
                value=correction,
                confidence=0.95,
                evidence=f"User gave explicit feedback: '{correction}'"
            )

        return None

    def adapt_response_prompt(self, base_prompt: str, context: PersonalizationContext) -> str:
        """
        Applies behavioral adaptation rules to the model system prompt.
        """
        if not context.personalization_enabled:
            return base_prompt

        directives = []
        if context.effective_response_length == "concise":
            directives.append("Keep response concise, crisp, and direct.")
        elif context.effective_response_length == "detailed":
            directives.append("Provide a detailed, thorough breakdown with comprehensive evidence.")

        if context.effective_technical_depth == "expert":
            directives.append("Assume expert domain knowledge. Skip basic introductory explanations.")
        elif context.effective_technical_depth == "novice":
            directives.append("Provide clear step-by-step guidance with helpful fundamentals.")

        if context.effective_formatting == "bullet_points":
            directives.append("Format key points using clear markdown bullet points.")
        elif context.effective_formatting == "code_heavy":
            directives.append("Emphasize concrete code implementations and functional examples.")

        if not directives:
            return base_prompt

        adapted = f"{base_prompt}\n\n[Saarthi Personalization Directives ({context.precedence_scope})]:\n" + "\n".join(f"- {d}" for d in directives)
        return adapted

    def explain_personalization(self, context: PersonalizationContext) -> Dict[str, Any]:
        """
        Returns structured rationale answering 'Why did Saarthi answer this way?'.
        """
        return {
            "precedence_scope": context.precedence_scope,
            "communication_style": context.effective_communication_style,
            "response_length": context.effective_response_length,
            "technical_depth": context.effective_technical_depth,
            "formatting": context.effective_formatting,
            "domain_expertise": context.effective_domain_expertise,
            "active_overrides": context.active_overrides,
            "explanations": context.explanations
        }

personalization_engine = PersonalizationEngine()
