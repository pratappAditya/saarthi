"""
Recency and Freshness Evaluation for Universal Research (Phase 7).
Categorizes sources into CURRENT, RECENT, HISTORICAL, and UNDATED.
Detects staleness, superseded standards, and documentation shifts.
Enforces the rule: Never present an old source as current merely because it is authoritative.
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from app.intelligence.research.evidence_models import RecencyCategory, SourceMetadata

# Current operational year anchor
CURRENT_YEAR = 2026

# Domains sensitive to rapid obsolescence
RAPID_OBSOLESCENCE_DOMAINS = [
    "cybersecurity", "software", "cs", "business", "career"
]

STALENESS_THRESHOLDS_YEARS = {
    "cybersecurity": 1,  # Vulnerabilities/threats > 1 yr may be obsolete or patched
    "software": 2,       # API docs > 2 yrs frequently contain breaking changes
    "business": 2,       # Market data / pricing > 2 yrs is historical
    "civil": 10,         # Building codes / standards have longer lifespan
    "mechanical": 10,
    "physics": 15,
    "archaeology": 50,   # Field excavation data remains primary historical evidence
    "history": 100
}


class RecencyHandler:
    @staticmethod
    def extract_year(date_str: Optional[str]) -> Optional[int]:
        if not date_str:
            return None
        match = re.search(r"\b(19\d\d|20\d\d)\b", str(date_str))
        if match:
            return int(match.group(1))
        return None

    @classmethod
    def classify_recency(
        cls,
        pub_date: Optional[str],
        domain: str = "general",
        is_historical_topic: bool = False
    ) -> Tuple[RecencyCategory, Optional[str]]:
        """
        Classifies publication date into CURRENT, RECENT, HISTORICAL, or UNDATED,
        and generates a staleness warning if applicable.
        """
        if not pub_date or str(pub_date).strip().lower() in ["none", "unknown", "n/a", ""]:
            return RecencyCategory.UNDATED, "Source is undated; corroborate claims with timestamped evidence."

        year = cls.extract_year(pub_date)
        if not year:
            return RecencyCategory.UNDATED, "Could not reliably extract publication year."

        delta_years = CURRENT_YEAR - year

        if delta_years <= 1:
            recency = RecencyCategory.CURRENT
        elif delta_years <= 3:
            recency = RecencyCategory.RECENT
        else:
            recency = RecencyCategory.HISTORICAL

        # Staleness analysis
        warning = None
        threshold = STALENESS_THRESHOLDS_YEARS.get(domain, 3)

        if not is_historical_topic and delta_years > threshold:
            if domain in ["software", "cybersecurity"]:
                warning = f"Source is from {year} ({delta_years} years old). APIs, CVE remediations, or security standards may be superseded."
            elif domain == "business":
                warning = f"Source is from {year}. Financial or market indicators are historical and may not reflect current conditions."
            else:
                warning = f"Source publication date is {year}; newer peer-reviewed literature or updated standards may supersede these findings."

        return recency, warning

    @classmethod
    def evaluate_source(
        cls,
        source: SourceMetadata,
        domain: str = "general",
        user_requested_current: bool = False
    ) -> SourceMetadata:
        """
        Applies recency classification and staleness checks to a source.
        """
        recency, staleness = cls.classify_recency(
            source.publication_date,
            domain=domain,
            is_historical_topic=(domain in ["history", "archaeology"])
        )
        source.recency = recency
        source.staleness_warning = staleness

        if user_requested_current and recency in [RecencyCategory.HISTORICAL, RecencyCategory.UNDATED]:
            if source.staleness_warning:
                source.staleness_warning += " [CAUTION: User requested current data; this historical source cannot serve as primary basis for current status.]"
            else:
                source.staleness_warning = "CAUTION: User requested current information; this source does not establish present-day status."

        return source


recency_handler = RecencyHandler()
