"""
Locked Canonical Plan Registry & Plan Versioning (Phase 10).
Defines and enforces fixed pricing across Saarthi.
Protects against price tampering and supports versioned plan snapshots.
"""

from typing import Dict, Any, List, Optional
from app.billing.models import PlanId, PlanDefinition, BillingInterval
from app.core.plans import PlanService


CANONICAL_PLAN_PRICING = {
    PlanId.FREE: {
        "name": "Saarthi Free",
        "price_inr": 0,
        "billing_interval": BillingInterval.FOREVER,
        "description": "Essential local AI operating companion with basic chat and career tools.",
        "badge": "Free",
        "is_custom": False,
        "version": "v1.0"
    },
    PlanId.STUDENT: {
        "name": "Saarthi Student",
        "price_inr": 99,
        "billing_interval": BillingInterval.MONTH,
        "description": "For students & learners with study workspaces and guided research.",
        "badge": "Student",
        "is_custom": False,
        "version": "v1.0"
    },
    PlanId.PERSONAL: {
        "name": "Saarthi Personal",
        "price_inr": 399,
        "billing_interval": BillingInterval.MONTH,
        "description": "Full personal AI companion with long-term memory, voice, and automations.",
        "badge": "Popular",
        "is_custom": False,
        "version": "v1.0"
    },
    PlanId.POWER: {
        "name": "Saarthi Power",
        "price_inr": 799,
        "billing_interval": BillingInterval.MONTH,
        "description": "For developers, researchers, and power users with terminal, computer control, and custom agents.",
        "badge": "Pro",
        "is_custom": False,
        "version": "v1.0"
    },
    PlanId.TEAMS: {
        "name": "Saarthi Teams",
        "price_inr": 699,
        "billing_interval": BillingInterval.USER_MONTH,
        "description": "Shared workspace, team memory, RBAC, and collaborative agent workflows.",
        "badge": "Teams",
        "is_custom": False,
        "version": "v1.0"
    },
    PlanId.ENTERPRISE: {
        "name": "Saarthi Enterprise",
        "price_inr": 0,  # Custom negotiated pricing
        "billing_interval": BillingInterval.CUSTOM,
        "description": "Dedicated infrastructure, SAML/SSO, audit logs, and custom domain packs.",
        "badge": "Enterprise",
        "is_custom": True,
        "version": "v1.0"
    }
}


class PlanRegistry:
    def __init__(self):
        self._versions: Dict[str, Dict[str, PlanDefinition]] = {}  # plan_id -> version -> PlanDefinition
        self._init_registry()

    def _init_registry(self):
        """Initializes canonical v1.0 plan definitions with capabilities and limits from PlanService."""
        for plan_id, info in CANONICAL_PLAN_PRICING.items():
            plan_key = plan_id.value.lower()
            caps = list(PlanService.get_capabilities_for_plan(plan_key).keys())
            limits = PlanService.get_limits_for_plan(plan_key)

            defn = PlanDefinition(
                plan_id=plan_id,
                name=info["name"],
                version=info["version"],
                price_inr=info["price_inr"],
                currency="INR",
                billing_interval=info["billing_interval"],
                description=info["description"],
                badge=info["badge"],
                is_custom=info["is_custom"],
                limits=limits,
                capabilities=caps
            )
            self._versions.setdefault(plan_id.value, {})[info["version"]] = defn

    def get_plan(self, plan_id: str, version: str = "v1.0") -> Optional[PlanDefinition]:
        """Fetches a specific version of a plan definition."""
        pid = plan_id.upper()
        versions = self._versions.get(pid, {})
        return versions.get(version) or versions.get("v1.0")

    def get_all_plans(self) -> List[PlanDefinition]:
        """Returns all current canonical plans."""
        return [self.get_plan(pid.value) for pid in PlanId if self.get_plan(pid.value)]

    def list_plans(self) -> List[PlanDefinition]:
        """Alias for get_all_plans."""
        return self.get_all_plans()

    def create_enterprise_custom_plan(
        self,
        client_name: str,
        negotiated_price_inr: int,
        seat_limit: int = 50,
        custom_capabilities: Optional[Dict[str, Any]] = None,
        custom_limits: Optional[Dict[str, Any]] = None,
        version: str = "v1.0"
    ) -> PlanDefinition:
        """Constructs a custom enterprise plan configuration for negotiated contracts."""
        caps = list(PlanService.get_capabilities_for_plan("enterprise").keys())
        if custom_capabilities:
            caps.extend(list(custom_capabilities.keys()))
        limits = PlanService.get_limits_for_plan("enterprise").copy()
        if custom_limits:
            limits.update(custom_limits)
        limits["seat_limit"] = seat_limit

        custom_defn = PlanDefinition(
            plan_id=PlanId.ENTERPRISE,
            name=f"Enterprise ({client_name})",
            version=version,
            price_inr=negotiated_price_inr,
            currency="INR",
            billing_interval=BillingInterval.MONTH,
            description=f"Custom Enterprise agreement for {client_name}",
            badge="Custom",
            is_custom=True,
            seat_limit=seat_limit,
            limits=limits,
            capabilities=caps
        )
        return custom_defn

    def get_catalog_dict(self) -> Dict[str, Any]:
        """Produces a JSON-serializable dictionary representation of the plan catalog."""
        return {
            "plans": [
                {
                    "id": p.plan_id.value,
                    "name": p.name,
                    "price_inr": p.price_inr,
                    "currency": p.currency,
                    "interval": p.billing_interval.value,
                    "badge": p.badge,
                    "description": p.description,
                    "is_custom": p.is_custom,
                    "version": p.version,
                    "capabilities": p.capabilities,
                    "limits": p.limits
                }
                for p in self.get_all_plans()
            ]
        }

    def calculate_expected_amount_paise(self, plan_id: str, seats: int = 1, version: str = "v1.0") -> int:
        """
        Calculates the canonical server-authoritative price in paise (1 INR = 100 paise).
        Prevents client-side price tampering.
        """
        defn = self.get_plan(plan_id, version=version)
        if not defn:
            raise ValueError(f"Unknown plan: '{plan_id}'")

        if defn.is_custom:
            return 0  # Enterprise custom pricing negotiated out-of-band

        seat_multiplier = max(1, seats) if defn.billing_interval == BillingInterval.USER_MONTH else 1
        return defn.price_inr * seat_multiplier * 100

    def validate_amount(self, plan_id: str, seats: int, provided_amount_paise: int, version: str = "v1.0") -> bool:
        """Strict server validation: provided amount must match expected canonical amount exactly."""
        expected = self.calculate_expected_amount_paise(plan_id, seats=seats, version=version)
        return expected == provided_amount_paise

    def register_plan_version(self, plan_definition: PlanDefinition):
        """Allows registering a new snapshot/version of a plan without altering historical definitions."""
        self._versions.setdefault(plan_definition.plan_id.value, {})[plan_definition.version] = plan_definition


plan_registry = PlanRegistry()
