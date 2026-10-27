"""
Hardware-Aware Nemotron Recommendation Engine for Saarthi.
Evaluates local HardwareProfile against the catalog tiers (STANDARD, PRO, SUPER, ULTRA)
to select the highest safe compatible tier and model.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.system.hardware import HardwareProfile, CompatibilityResult, CompatibilityStatus
from app.models.nemotron_catalog import NemotronModelCatalog, NemotronModelSpec

class RecommendationOutput(BaseModel):
    recommended_tier: str
    recommended_model: NemotronModelSpec
    reason: str
    compatibility: Dict[str, CompatibilityResult]
    hardware_summary: HardwareProfile
    alternative_models: List[NemotronModelSpec]

class NemotronRecommendationService:
    @classmethod
    def check_model_compatibility(cls, spec: NemotronModelSpec, profile: HardwareProfile) -> CompatibilityResult:
        """
        Evaluates a single NemotronModelSpec against a HardwareProfile.
        """
        warnings = []
        ram = profile.total_ram_gb
        vram = profile.vram_gb
        storage = profile.free_storage_gb

        if ram < spec.minimum_ram_gb:
            return CompatibilityResult(
                status=CompatibilityStatus.INSUFFICIENT_RAM,
                compatible=False,
                recommended=False,
                reason=f"Requires minimum {spec.minimum_ram_gb} GB RAM (System has {ram} GB)."
            )

        if storage < spec.minimum_storage_gb:
            return CompatibilityResult(
                status=CompatibilityStatus.INSUFFICIENT_STORAGE,
                compatible=False,
                recommended=False,
                reason=f"Requires {spec.minimum_storage_gb} GB free storage (System has {storage} GB)."
            )

        if spec.minimum_vram_gb > 0 and vram < spec.minimum_vram_gb:
            return CompatibilityResult(
                status=CompatibilityStatus.INSUFFICIENT_VRAM,
                compatible=False,
                recommended=False,
                reason=f"Requires dedicated GPU with at least {spec.minimum_vram_gb} GB VRAM (System has {vram} GB)."
            )

        # Warnings for minimum vs recommended
        if ram < spec.recommended_ram_gb:
            warnings.append(f"RAM ({ram} GB) meets minimum ({spec.minimum_ram_gb} GB) but is below recommended {spec.recommended_ram_gb} GB.")

        if spec.recommended_vram_gb > 0 and vram < spec.recommended_vram_gb:
            warnings.append(f"VRAM ({vram} GB) is below recommended {spec.recommended_vram_gb} GB for optimal inference.")

        status = CompatibilityStatus.RECOMMENDED if not warnings else CompatibilityStatus.MINIMUM_ONLY

        return CompatibilityResult(
            status=status,
            compatible=True,
            recommended=(status == CompatibilityStatus.RECOMMENDED),
            reason="System specifications satisfy all hardware requirements.",
            warnings=warnings
        )

    @classmethod
    def recommend_nemotron_model(cls, profile: Optional[HardwareProfile] = None, user_plan: str = "POWER") -> RecommendationOutput:
        """
        Main recommendation engine logic.
        Prefers highest tier reliably supported and permitted by subscription (ULTRA > SUPER > PRO > STANDARD).
        NOTE: ULTRA tier access requires BOTH POWER subscription AND ULTRA hardware capability.
        """
        if profile is None:
            from app.system.hardware import HardwareDetectionService
            profile = HardwareDetectionService.get_hardware_profile()

        specs = NemotronModelCatalog.get_all_specs()
        compatibility_map: Dict[str, CompatibilityResult] = {}
        compatible_specs: List[NemotronModelSpec] = []

        for spec in specs:
            comp = cls.check_model_compatibility(spec, profile)
            # Enforce dual-qualification for ULTRA tier
            if spec.tier == "ULTRA" and user_plan.upper() != "POWER":
                comp = CompatibilityResult(
                    status=CompatibilityStatus.INSUFFICIENT_RAM,
                    compatible=False,
                    recommended=False,
                    reason="ULTRA model tier requires an active POWER subscription."
                )
            compatibility_map[spec.tier] = comp
            if comp.compatible:
                compatible_specs.append(spec)

        # Hierarchy: ULTRA -> SUPER -> PRO -> STANDARD
        tier_hierarchy = ["ULTRA", "SUPER", "PRO", "STANDARD"]
        recommended_spec: Optional[NemotronModelSpec] = None
        rec_reason = ""

        # Safe recommendation selection
        for tier in tier_hierarchy:
            spec = NemotronModelCatalog.get_spec_by_tier(tier)
            if spec and compatibility_map.get(tier, CompatibilityResult(
                status=CompatibilityStatus.INSUFFICIENT_RAM, compatible=False, recommended=False, reason=""
            )).compatible:
                recommended_spec = spec
                if tier == "ULTRA":
                    rec_reason = "POWER Subscription & High-end Workstation GPU detected. Recommending ULTRA tier for maximum performance."
                elif tier == "SUPER":
                    rec_reason = "Strong Workstation PC detected. Recommending SUPER tier for optimal reasoning and speed balance."
                elif tier == "PRO":
                    rec_reason = "Standard PC specs detected. Recommending PRO tier for reliable local career assistant features."
                else:
                    rec_reason = "Compact System specs detected. Recommending STANDARD tier for lightweight execution."
                break

        # Fallback if none fully compatible
        if not recommended_spec:
            recommended_spec = NemotronModelCatalog.get_spec_by_tier("STANDARD") or specs[0]
            rec_reason = "System memory/storage is constrained. Conservative Standard tier selected for initial setup."

        alternatives = [s for s in specs if s.model_id != recommended_spec.model_id]

        return RecommendationOutput(
            recommended_tier=recommended_spec.tier,
            recommended_model=recommended_spec,
            reason=rec_reason,
            compatibility=compatibility_map,
            hardware_summary=profile,
            alternative_models=alternatives
        )
