"""Annual, state-aware scenario planning for a 25-year simulated marriage."""

import math
import random
from collections import Counter
from typing import Dict, Iterable, List, Optional, Sequence

from pydantic import BaseModel, Field

from scenario_catalog import ScenarioDefinition
from scenario_ontology import DOMAIN_ALLOCATIONS, ScenarioDomain
from state_models import (
    LifePhase,
    LifeState,
    MarriageState,
    NarrativeState,
    ScenarioHistoryRecord,
)


class ScenarioBudget(BaseModel):
    min_total: int = 50
    target_total: int = 90
    max_total: int = 150
    total_used: int = 0
    positive_count: int = 0
    severity_counts: Dict[str, int] = Field(default_factory=dict)
    domain_counts: Dict[str, int] = Field(default_factory=dict)

    @property
    def remaining_capacity(self) -> int:
        return max(0, self.max_total - self.total_used)

    def record(self, scenario: ScenarioDefinition) -> None:
        self.total_used += 1
        if scenario.positive:
            self.positive_count += 1
        severity_band = (
            "low" if scenario.severity < 0.3
            else "moderate" if scenario.severity < 0.55
            else "high" if scenario.severity < 0.8
            else "extreme"
        )
        self.severity_counts[severity_band] = self.severity_counts.get(severity_band, 0) + 1
        key = scenario.primary_domain.value
        self.domain_counts[key] = self.domain_counts.get(key, 0) + 1


class PlannerScore(BaseModel):
    scenario_id: str
    occurrence_probability: float
    life_phase_compatibility: float
    persona_relevance: float
    history_activation: float
    coverage_need: float
    diagnostic_value: float
    diversity_modifier: float
    final_weight: float


PHASE_EVENT_RANGES = {
    LifePhase.NEWLYWED: (2, 5),
    LifePhase.CAREER_BUILDING: (3, 6),
    LifePhase.CHILDCARE: (3, 8),
    LifePhase.ESTABLISHED_FAMILY: (2, 6),
    LifePhase.MIDLIFE: (2, 7),
    LifePhase.DUAL_CAREGIVING: (2, 7),
    LifePhase.MATURE_PARTNERSHIP: (2, 5),
}


PHASE_DOMAIN_WEIGHTS = {
    LifePhase.NEWLYWED: {
        ScenarioDomain.HOUSEHOLD_LIFESTYLE: 1.6,
        ScenarioDomain.COMMUNICATION_CONFLICT: 1.35,
        ScenarioDomain.FAMILY_IN_LAWS: 1.35,
        ScenarioDomain.SEX_AFFECTION_INTIMACY: 1.25,
        ScenarioDomain.PARENTING_FERTILITY: 0.35,
        ScenarioDomain.HEALTH_CAREGIVING_GRIEF: 0.45,
    },
    LifePhase.CAREER_BUILDING: {
        ScenarioDomain.CAREER_RELOCATION: 1.55,
        ScenarioDomain.MONEY_ASSETS_DEBT: 1.45,
        ScenarioDomain.FAMILY_IN_LAWS: 1.2,
        ScenarioDomain.PARENTING_FERTILITY: 1.15,
    },
    LifePhase.CHILDCARE: {
        ScenarioDomain.PARENTING_FERTILITY: 1.8,
        ScenarioDomain.HOUSEHOLD_LIFESTYLE: 1.35,
        ScenarioDomain.SEX_AFFECTION_INTIMACY: 1.3,
        ScenarioDomain.CAREER_RELOCATION: 1.2,
    },
    LifePhase.ESTABLISHED_FAMILY: {
        ScenarioDomain.PARENTING_FERTILITY: 1.35,
        ScenarioDomain.MONEY_ASSETS_DEBT: 1.25,
        ScenarioDomain.EMOTIONAL_CONNECTION: 1.25,
    },
    LifePhase.MIDLIFE: {
        ScenarioDomain.EMOTIONAL_CONNECTION: 1.35,
        ScenarioDomain.CAREER_RELOCATION: 1.3,
        ScenarioDomain.HEALTH_CAREGIVING_GRIEF: 1.25,
        ScenarioDomain.SEX_AFFECTION_INTIMACY: 1.2,
    },
    LifePhase.DUAL_CAREGIVING: {
        ScenarioDomain.HEALTH_CAREGIVING_GRIEF: 1.65,
        ScenarioDomain.PARENTING_FERTILITY: 1.35,
        ScenarioDomain.MONEY_ASSETS_DEBT: 1.25,
    },
    LifePhase.MATURE_PARTNERSHIP: {
        ScenarioDomain.HEALTH_CAREGIVING_GRIEF: 1.5,
        ScenarioDomain.EMOTIONAL_CONNECTION: 1.35,
        ScenarioDomain.MONEY_ASSETS_DEBT: 1.25,
        ScenarioDomain.IDENTITY_RELIGION_CULTURE: 1.2,
    },
}


def _trait_value(persona: dict, trait: str) -> float:
    value = persona.get("traits", {}).get(trait, 0.5)
    if isinstance(value, dict):
        value = value.get("mean", 0.5)
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.5


def _trait_uncertainty(persona: dict, trait: str) -> float:
    value = persona.get("traits", {}).get(trait, {})
    if not isinstance(value, dict):
        return 0.25
    variance = max(0.0, float(value.get("variance", 0.02)))
    confidence = max(0.0, min(1.0, float(value.get("confidence", 0.5))))
    return min(1.0, math.sqrt(variance) + (1.0 - confidence) * 0.5)


def scenario_is_eligible(scenario: ScenarioDefinition, life_state: LifeState) -> bool:
    if not scenario.min_year <= life_state.year <= scenario.max_year:
        return False

    rules = scenario.eligibility
    if (
        life_state.plans.get("children_intent") == "childfree"
        and scenario.primary_domain == ScenarioDomain.PARENTING_FERTILITY
        and "children_decision" not in scenario.family_id
    ):
        return False
    if rules.get("has_children") is True and not life_state.has_children:
        return False
    if rules.get("childfree") is True and life_state.plans.get("children_intent") != "childfree":
        return False
    if rules.get("any_parent_alive") is True:
        parents = life_state.parents_a + life_state.parents_b
        if not any(parent.alive for parent in parents):
            return False
    if rules.get("either_partner_employed") is True:
        if not (life_state.career_a.employed or life_state.career_b.employed):
            return False
    required_flags = set(rules.get("required_flags", []))
    forbidden_flags = set(rules.get("forbidden_flags", []))
    actual_flags = set(life_state.flags)
    if not required_flags.issubset(actual_flags):
        return False
    if forbidden_flags & actual_flags:
        return False
    return True


class AnnualScenarioPlanner:
    def __init__(self, catalog: Sequence[ScenarioDefinition], seed: Optional[int] = None):
        self.catalog = tuple(catalog)
        self.random = random.Random(seed)

    def determine_event_count(
        self,
        life_state: LifeState,
        marriage_state: MarriageState,
        history: Sequence[ScenarioHistoryRecord],
        budget: ScenarioBudget,
    ) -> int:
        low, high = PHASE_EVENT_RANGES[life_state.phase]
        unresolved_load = sum(1 for injury in marriage_state.injuries if not injury.resolved)
        history_load = sum(1 for item in history if item.year >= life_state.year - 2 and item.outcome == "injury")
        transition_load = int(any(flag.endswith("_transition") for flag in life_state.flags))
        count = self.random.randint(low, high)
        count += min(2, (unresolved_load + history_load + transition_load) // 3)

        remaining_years_after_this = max(0, 25 - life_state.year)
        minimum_needed = max(0, budget.min_total - budget.total_used)
        minimum_now = max(0, minimum_needed - remaining_years_after_this * 8)

        target_needed = max(0, budget.target_total - budget.total_used)
        target_pace = math.ceil(target_needed / (remaining_years_after_this + 1))
        if budget.total_used < budget.target_total:
            # Keep stochastic life-load variation, but steer gently toward the
            # global target instead of blindly accumulating the phase maxima.
            count = min(count, max(1, target_pace + 1))
            count = max(count, min(target_pace, high))
        else:
            count = min(count, 1)

        return max(0, min(8, count, budget.remaining_capacity, max(minimum_now, 0) + 8))

    def score_scenario(
        self,
        scenario: ScenarioDefinition,
        persona_a: dict,
        persona_b: dict,
        life_state: LifeState,
        history: Sequence[ScenarioHistoryRecord],
        budget: ScenarioBudget,
        selected_family_ids: Iterable[str] = (),
    ) -> PlannerScore:
        if not scenario_is_eligible(scenario, life_state):
            diversity = 0.0
        else:
            family_years = [item.year for item in history if item.family_id == scenario.family_id]
            latest_year = max(family_years, default=-100)
            diversity = 0.0 if (
                scenario.family_id in set(selected_family_ids)
                or latest_year + scenario.cooldown_years > life_state.year
            ) else 1.0

        phase_weight = PHASE_DOMAIN_WEIGHTS.get(life_state.phase, {}).get(
            scenario.primary_domain, 1.0
        )

        divergences = [
            abs(_trait_value(persona_a, trait) - _trait_value(persona_b, trait))
            for trait in scenario.traits
        ]
        uncertainties = [
            (_trait_uncertainty(persona_a, trait) + _trait_uncertainty(persona_b, trait)) / 2
            for trait in scenario.traits
        ]
        divergence = sum(divergences) / len(divergences) if divergences else 0.0
        uncertainty = sum(uncertainties) / len(uncertainties) if uncertainties else 0.0
        persona_relevance = 0.65 + divergence * 0.75 + uncertainty * 0.25

        activated = Counter(
            followup
            for item in history
            for followup in item.activated_followups
        )
        tag_overlap = sum(
            len(set(item.memory_tags) & set(scenario.memory_tags))
            for item in history[-12:]
        )
        history_activation = 1.0 + min(2.0, activated[scenario.family_id] * 0.7 + tag_overlap * 0.08)

        used = budget.domain_counts.get(scenario.primary_domain.value, 0)
        expected_share = DOMAIN_ALLOCATIONS[scenario.primary_domain] / 1000.0
        expected_used = max(1.0, budget.total_used * expected_share)
        coverage_need = max(0.65, min(1.8, expected_used / max(1.0, used)))
        if budget.total_used and scenario.positive and budget.positive_count / budget.total_used < 0.20:
            coverage_need *= 1.25

        early = max(0.0, min(1.0, (10 - life_state.year) / 9.0))
        persona_exponent = 0.75 + 0.6 * early
        history_exponent = 1.6 - 1.1 * early
        occurrence = scenario.base_probability
        final_weight = (
            occurrence
            * phase_weight
            * (persona_relevance ** persona_exponent)
            * (history_activation ** history_exponent)
            * coverage_need
            * (0.55 + scenario.diagnostic_value)
            * diversity
        )

        return PlannerScore(
            scenario_id=scenario.id,
            occurrence_probability=occurrence,
            life_phase_compatibility=phase_weight,
            persona_relevance=persona_relevance,
            history_activation=history_activation,
            coverage_need=coverage_need,
            diagnostic_value=scenario.diagnostic_value,
            diversity_modifier=diversity,
            final_weight=max(0.0, final_weight),
        )

    def plan_year(
        self,
        persona_a: dict,
        persona_b: dict,
        marriage_state: MarriageState,
        life_state: LifeState,
        narrative_state: NarrativeState,
        history: Sequence[ScenarioHistoryRecord],
        budget: ScenarioBudget,
    ) -> List[ScenarioDefinition]:
        del narrative_state  # Reserved for narrative-specific modifiers.
        event_count = self.determine_event_count(life_state, marriage_state, history, budget)
        selected: List[ScenarioDefinition] = []
        selected_families: set[str] = set()

        for _ in range(event_count):
            candidates: List[ScenarioDefinition] = []
            weights: List[float] = []
            for scenario in self.catalog:
                score = self.score_scenario(
                    scenario,
                    persona_a,
                    persona_b,
                    life_state,
                    history,
                    budget,
                    selected_families,
                )
                if score.final_weight > 0.0:
                    candidates.append(scenario)
                    weights.append(score.final_weight)

            if not candidates:
                break
            chosen = self.random.choices(candidates, weights=weights, k=1)[0]
            selected.append(chosen)
            selected_families.add(chosen.family_id)

        return selected
