"""Validated, hierarchical 1,000-item life-scenario catalog.

The source of truth is roughly 120 scenario families.  Concrete variants are
compiled deterministically so catalog size, positive-event share, and ontology
coverage cannot drift between deployments.
"""

from collections import Counter
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator

from scenario_ontology import (
    DOMAIN_ALLOCATIONS,
    DOMAIN_CATEGORY,
    DOMAIN_DIMENSIONS,
    MEMORY_TAGS,
    NEEDS,
    PROVISIONS,
    SAFETY_FLAGS,
    TRAITS,
    VALUES,
    ScenarioDomain,
)


class ScenarioRole(str, Enum):
    STRESSOR = "stressor"
    OPPORTUNITY = "opportunity"
    TRANSITION = "transition"
    REPAIR = "repair"
    SAFETY = "safety"


class SimulationDepth(str, Enum):
    LIGHT = "light"
    NORMAL = "normal"
    DEEP = "deep"


class ScenarioDefinition(BaseModel):
    id: str
    family_id: str
    variant: int
    title: str
    description: str
    role: ScenarioRole
    primary_domain: ScenarioDomain
    secondary_domains: List[ScenarioDomain] = Field(default_factory=list)
    category: str
    base_probability: float = Field(ge=0.0, le=1.0)
    diagnostic_value: float = Field(ge=0.0, le=1.0)
    severity: float = Field(ge=0.0, le=1.0)
    positive: bool = False
    safety_relevant: bool = False
    safety_flags: List[str] = Field(default_factory=list)
    min_year: int = Field(ge=1, le=25)
    max_year: int = Field(ge=1, le=25)
    traits: List[str]
    values: List[str]
    needs_activated: List[str]
    provisions_tested: List[str]
    memory_tags: List[str]
    eligibility: Dict[str, Any] = Field(default_factory=dict)
    probability_modifiers: Dict[str, float] = Field(default_factory=dict)
    followup_family_ids: List[str] = Field(default_factory=list)
    repeatable: bool = True
    cooldown_years: int = Field(ge=0, le=25)
    simulation_depth: SimulationDepth

    @validator("traits")
    def valid_traits(cls, value: List[str]) -> List[str]:
        unknown = set(value) - TRAITS
        if unknown:
            raise ValueError(f"unknown traits: {sorted(unknown)}")
        return value

    @validator("values")
    def valid_values(cls, values_: List[str]) -> List[str]:
        unknown = set(values_) - VALUES
        if unknown:
            raise ValueError(f"unknown values: {sorted(unknown)}")
        return values_

    @validator("needs_activated")
    def valid_needs(cls, values_: List[str]) -> List[str]:
        unknown = set(values_) - NEEDS
        if unknown:
            raise ValueError(f"unknown needs: {sorted(unknown)}")
        return values_

    @validator("provisions_tested")
    def valid_provisions(cls, values_: List[str]) -> List[str]:
        unknown = set(values_) - PROVISIONS
        if unknown:
            raise ValueError(f"unknown provisions: {sorted(unknown)}")
        return values_

    @validator("memory_tags")
    def valid_memory_tags(cls, values_: List[str]) -> List[str]:
        unknown = set(values_) - MEMORY_TAGS
        if unknown:
            raise ValueError(f"unknown memory tags: {sorted(unknown)}")
        return values_

    @validator("safety_flags")
    def valid_safety_flags(cls, values_: List[str]) -> List[str]:
        unknown = set(values_) - SAFETY_FLAGS
        if unknown:
            raise ValueError(f"unknown safety flags: {sorted(unknown)}")
        return values_

    def to_engine_dict(self) -> dict:
        """Return the legacy dictionary shape consumed by simulation_engine."""
        signed_severity = -self.severity if self.positive else self.severity
        weight = 1 if self.severity < 0.34 else 2 if self.severity < 0.7 else 3
        payload = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        payload.update({
            "role": self.role.value,
            "primary_domain": self.primary_domain.value,
            "secondary_domains": [domain.value for domain in self.secondary_domains],
            "simulation_depth": self.simulation_depth.value,
        })
        return {
            **payload,
            "severity": signed_severity,
            "magnitude": self.severity,
            "weight": weight,
            "dealbreaker": self.safety_relevant and self.severity >= 0.7,
            "domains": [self.primary_domain.value] + [d.value for d in self.secondary_domains],
            "traits_relevant": self.traits,
            "needs_triggered": self.needs_activated,
            "test_reason": "Tests " + ", ".join(self.traits),
            "scoring_logic": "Evaluate mutuality, safety, repair, and state consequences.",
        }


FAMILY_NAMES = {
    ScenarioDomain.HOUSEHOLD_LIFESTYLE: [
        "household labor split", "cleanliness standards", "meal planning",
        "sleep schedules", "personal space", "guest hosting", "pet care",
        "home maintenance", "shared leisure", "new home ritual",
    ],
    ScenarioDomain.EMOTIONAL_CONNECTION: [
        "missed emotional bid", "quality time drift", "friendship maintenance",
        "celebrating achievement", "emotional disclosure", "loneliness in company",
        "shared humor", "romantic initiative", "gratitude practice", "reconnection trip",
    ],
    ScenarioDomain.COMMUNICATION_CONFLICT: [
        "criticism escalation", "withdrawal after conflict", "repair attempt",
        "recurring argument", "public disagreement", "decision deadlock",
        "apology quality", "tone misinterpretation", "problem solving under stress",
        "successful hard conversation",
    ],
    ScenarioDomain.FAMILY_IN_LAWS: [
        "parental criticism", "parent staying with couple", "holiday allocation",
        "family privacy intrusion", "sibling obligation", "elder boundary",
        "public family loyalty test", "family caregiving expectation",
        "parent appreciates spouse", "families cooperate",
    ],
    ScenarioDomain.MONEY_ASSETS_DEBT: [
        "large family loan", "hidden debt", "joint budget", "major purchase",
        "investment risk", "income imbalance", "inheritance decision",
        "financial control", "savings milestone", "unexpected windfall",
    ],
    ScenarioDomain.CAREER_RELOCATION: [
        "promotion workload", "relocation offer", "career sacrifice", "layoff",
        "startup gamble", "work travel", "professional jealousy", "return to work",
        "award recognition", "shared career breakthrough",
    ],
    ScenarioDomain.PARENTING_FERTILITY: [
        "children decision", "fertility treatment", "pregnancy transition", "newborn care",
        "childcare labor", "discipline disagreement", "school choice", "teen boundaries",
        "child milestone", "parenting teamwork win",
    ],
    ScenarioDomain.TRUST_JEALOUSY: [
        "close friendship boundary", "phone privacy", "former partner contact",
        "workplace attraction", "secret keeping", "social media jealousy",
        "infidelity disclosure", "monitoring behavior", "earned trust milestone",
        "vulnerability rewarded",
    ],
    ScenarioDomain.SEX_AFFECTION_INTIMACY: [
        "desire discrepancy", "affection mismatch", "body image vulnerability",
        "sexual boundary", "postpartum intimacy", "routine and novelty",
        "rejection repair", "medical intimacy change", "honest desire conversation",
        "renewed affection",
    ],
    ScenarioDomain.HEALTH_CAREGIVING_GRIEF: [
        "acute illness", "chronic diagnosis", "mental health strain", "parental illness",
        "caregiving burnout", "bereavement", "health behavior conflict", "disability adaptation",
        "recovery milestone", "care received with gratitude",
    ],
    ScenarioDomain.IDENTITY_RELIGION_CULTURE: [
        "religious observance", "conversion pressure", "language and culture",
        "gender role expectation", "caste or community pressure", "political values",
        "identity evolution", "festival practice", "blended tradition", "shared meaning",
    ],
    ScenarioDomain.MAJOR_CRISIS: [
        "natural disaster", "serious accident", "legal crisis", "forced displacement",
        "violent family threat", "addiction crisis", "custody threat", "business collapse",
        "crisis teamwork", "community rescue",
    ],
}

SETTINGS = (
    "a private evening at home", "a family dinner", "a rushed workday morning",
    "a holiday gathering", "a financial planning meeting", "a medical appointment",
    "a school meeting", "a visit from relatives", "a long-planned trip",
    "a period of unusually high workload", "a public social event", "a quiet weekend",
)

STAKES = (
    "the couple's sense of fairness", "one partner's dignity", "financial security",
    "family harmony", "career momentum", "trust", "privacy", "physical wellbeing",
    "their shared future plan", "the ability to feel like a team",
)

TRADEOFFS = {
    ScenarioDomain.HOUSEHOLD_LIFESTYLE: "personal comfort and equitable shared labor",
    ScenarioDomain.EMOTIONAL_CONNECTION: "individual bandwidth and emotional responsiveness",
    ScenarioDomain.COMMUNICATION_CONFLICT: "short-term peace and honest long-term resolution",
    ScenarioDomain.FAMILY_IN_LAWS: "family harmony and protection of the couple boundary",
    ScenarioDomain.MONEY_ASSETS_DEBT: "autonomy or family duty and shared financial security",
    ScenarioDomain.CAREER_RELOCATION: "one career opportunity and the other partner's stability",
    ScenarioDomain.PARENTING_FERTILITY: "individual limits and the couple's parenting commitments",
    ScenarioDomain.TRUST_JEALOUSY: "privacy and the reassurance needed to sustain trust",
    ScenarioDomain.SEX_AFFECTION_INTIMACY: "personal boundaries and mutual intimate connection",
    ScenarioDomain.HEALTH_CAREGIVING_GRIEF: "caregiving duty and sustainable personal capacity",
    ScenarioDomain.IDENTITY_RELIGION_CULTURE: "authentic identity and shared cultural belonging",
    ScenarioDomain.MAJOR_CRISIS: "immediate survival needs and protection of the partnership",
}

YEAR_RANGES = {
    ScenarioDomain.HOUSEHOLD_LIFESTYLE: (1, 25),
    ScenarioDomain.EMOTIONAL_CONNECTION: (1, 25),
    ScenarioDomain.COMMUNICATION_CONFLICT: (1, 25),
    ScenarioDomain.FAMILY_IN_LAWS: (1, 25),
    ScenarioDomain.MONEY_ASSETS_DEBT: (2, 25),
    ScenarioDomain.CAREER_RELOCATION: (2, 22),
    ScenarioDomain.PARENTING_FERTILITY: (2, 24),
    ScenarioDomain.TRUST_JEALOUSY: (1, 25),
    ScenarioDomain.SEX_AFFECTION_INTIMACY: (1, 25),
    ScenarioDomain.HEALTH_CAREGIVING_GRIEF: (4, 25),
    ScenarioDomain.IDENTITY_RELIGION_CULTURE: (1, 25),
    ScenarioDomain.MAJOR_CRISIS: (1, 25),
}


def _slug(value: str) -> str:
    return "_".join(value.lower().replace("/", " ").split())


def _family_id(domain: ScenarioDomain, family_name: str) -> str:
    return f"{domain.value}__{_slug(family_name)}"


def _eligibility(domain: ScenarioDomain, family_name: str) -> Dict[str, Any]:
    name = family_name.lower()
    rules: Dict[str, Any] = {}
    if domain == ScenarioDomain.PARENTING_FERTILITY and not any(
        token in name for token in ("children decision", "fertility", "pregnancy")
    ):
        rules["has_children"] = True
    if "parent" in name and domain != ScenarioDomain.PARENTING_FERTILITY:
        rules["any_parent_alive"] = True
    if domain == ScenarioDomain.CAREER_RELOCATION:
        rules["either_partner_employed"] = True
    return rules


def _safety_flags(family_name: str) -> List[str]:
    name = family_name.lower()
    mapping = {
        "financial control": "financial_abuse",
        "sexual boundary": "sexual_coercion",
        "monitoring": "coercive_control",
        "infidelity": "infidelity",
        "violent": "honor_violence",
        "addiction": "addiction_risk",
        "custody": "custody_threat",
    }
    return [flag for token, flag in mapping.items() if token in name]


@lru_cache(maxsize=1)
def build_catalog() -> tuple[ScenarioDefinition, ...]:
    catalog: List[ScenarioDefinition] = []
    global_index = 0

    for domain, allocation in DOMAIN_ALLOCATIONS.items():
        families = FAMILY_NAMES[domain]
        base_count, remainder = divmod(allocation, len(families))
        family_ids = [_family_id(domain, name) for name in families]
        dimensions = DOMAIN_DIMENSIONS[domain]
        min_year, max_year = YEAR_RANGES[domain]

        for family_index, family_name in enumerate(families):
            family_id = family_ids[family_index]
            variant_count = base_count + (1 if family_index < remainder else 0)
            followup = family_ids[(family_index + 1) % len(family_ids)]

            for variant in range(1, variant_count + 1):
                global_index += 1
                positive = global_index % 5 == 0
                safety_flags = [] if positive else _safety_flags(family_name)
                severity = round(0.16 + ((variant * 17 + family_index * 11) % 70) / 100, 2)
                if positive:
                    severity = round(min(0.55, 0.18 + (variant % 5) * 0.07), 2)
                    role = ScenarioRole.OPPORTUNITY
                    description = (
                        f"During {SETTINGS[(variant + family_index) % len(SETTINGS)]}, an "
                        f"unexpectedly positive turn involving {family_name} gives the couple "
                        f"a chance to celebrate, reciprocate support, and strengthen team identity."
                    )
                else:
                    role = ScenarioRole.SAFETY if safety_flags else ScenarioRole.STRESSOR
                    description = (
                        f"During {SETTINGS[(variant + family_index) % len(SETTINGS)]}, "
                        f"{family_name} becomes a concrete decision for the couple. They must "
                        f"balance {TRADEOFFS[domain]}, while "
                        f"{STAKES[(variant * 2 + family_index) % len(STAKES)]} is at risk."
                    )

                depth = (
                    SimulationDepth.DEEP if severity >= 0.72 or safety_flags
                    else SimulationDepth.NORMAL if severity >= 0.38
                    else SimulationDepth.LIGHT
                )
                base_probability = round(0.025 + ((variant + family_index) % 8) * 0.009, 3)
                diagnostic_value = round(0.48 + ((variant * 7 + family_index) % 45) / 100, 2)

                catalog.append(ScenarioDefinition(
                    id=f"{family_id}__v{variant:02d}",
                    family_id=family_id,
                    variant=variant,
                    title=f"{family_name.title()} — Variant {variant}",
                    description=description,
                    role=role,
                    primary_domain=domain,
                    category=DOMAIN_CATEGORY[domain],
                    base_probability=base_probability,
                    diagnostic_value=min(0.95, diagnostic_value),
                    severity=severity,
                    positive=positive,
                    safety_relevant=bool(safety_flags),
                    safety_flags=safety_flags,
                    min_year=min_year,
                    max_year=max_year,
                    traits=list(dimensions["traits"]),
                    values=list(dimensions["values"]),
                    needs_activated=list(dimensions["needs"]),
                    provisions_tested=list(dimensions["provisions"]),
                    memory_tags=list(dimensions["memory"]),
                    eligibility=_eligibility(domain, family_name),
                    probability_modifiers={
                        dimensions["traits"][0]: 1.35,
                        "prior_family_event": 1.45,
                    },
                    followup_family_ids=[followup],
                    repeatable=True,
                    cooldown_years=1 if positive else 2 + (family_index % 3),
                    simulation_depth=depth,
                ))

    validate_catalog(catalog)
    return tuple(catalog)


def validate_catalog(catalog: List[ScenarioDefinition] | tuple[ScenarioDefinition, ...]) -> None:
    if len(catalog) != 1000:
        raise ValueError(f"catalog must contain 1,000 scenarios, got {len(catalog)}")
    ids = [scenario.id for scenario in catalog]
    if len(set(ids)) != len(ids):
        raise ValueError("scenario IDs must be unique")
    positive_count = sum(s.positive for s in catalog)
    if positive_count != 200:
        raise ValueError(f"catalog must contain exactly 20% positive events, got {positive_count}")
    actual_allocations = Counter(s.primary_domain for s in catalog)
    if actual_allocations != Counter(DOMAIN_ALLOCATIONS):
        raise ValueError(f"domain allocation mismatch: {actual_allocations}")
    family_ids = {s.family_id for s in catalog}
    dangling = {
        followup
        for scenario in catalog
        for followup in scenario.followup_family_ids
        if followup not in family_ids
    }
    if dangling:
        raise ValueError(f"dangling follow-up families: {sorted(dangling)}")
    for scenario in catalog:
        if scenario.min_year > scenario.max_year:
            raise ValueError(f"invalid year range for {scenario.id}")


def get_catalog() -> tuple[ScenarioDefinition, ...]:
    return build_catalog()


def get_catalog_for_api() -> List[dict]:
    return [scenario.to_engine_dict() for scenario in get_catalog()]
