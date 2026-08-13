"""State transitions and Monte Carlo orchestration for adaptive 25-year lives."""

import random
from collections import Counter
from statistics import mean, median
from typing import Any, Callable, Dict, List, Optional, Sequence

from scenario_catalog import ScenarioDefinition, get_catalog
from scenario_ontology import ScenarioDomain
from scenario_planner import AnnualScenarioPlanner, ScenarioBudget, _trait_value
from state_models import (
    ChildState,
    LifeState,
    MarriageState,
    NarrativeState,
    ScenarioHistoryRecord,
    YearSnapshot,
)


POSITIVE_OUTCOMES = {"growth", "repair", "managed"}
DialogueRenderer = Callable[[dict, dict, ScenarioDefinition, MarriageState], List[dict]]


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _persona_children_intent(persona_a: dict, persona_b: dict) -> str:
    intents = [
        persona_a.get("life_plans", {}).get("children_intent"),
        persona_b.get("life_plans", {}).get("children_intent"),
    ]
    if "childfree" in intents:
        return "childfree"
    if "yes" in intents or "planned" in intents:
        return "planned"
    return "open"


class LongitudinalSimulator:
    def __init__(
        self,
        catalog: Optional[Sequence[ScenarioDefinition]] = None,
        seed: Optional[int] = None,
    ):
        self.catalog = tuple(catalog or get_catalog())
        self.seed = seed
        self.random = random.Random(seed)
        self.planner = AnnualScenarioPlanner(self.catalog, seed=seed)

    def _pair_capacity(self, persona_a: dict, persona_b: dict, scenario: ScenarioDefinition) -> float:
        capacity_traits = set(scenario.traits) | {
            "repair_skill", "co_regulation_capacity", "distress_tolerance"
        }
        partner_capacities = []
        for persona in (persona_a, persona_b):
            scores = [_trait_value(persona, trait) for trait in capacity_traits]
            partner_capacities.append(sum(scores) / len(scores))
        # A relationship is constrained by the weaker partner but allows some
        # compensation by the stronger partner.
        return min(partner_capacities) * 0.75 + max(partner_capacities) * 0.25

    def _alignment(self, persona_a: dict, persona_b: dict, scenario: ScenarioDefinition) -> float:
        if not scenario.traits:
            return 0.5
        return mean(
            1.0 - abs(_trait_value(persona_a, trait) - _trait_value(persona_b, trait))
            for trait in scenario.traits
        )

    def resolve_outcome(
        self,
        persona_a: dict,
        persona_b: dict,
        scenario: ScenarioDefinition,
        marriage_state: MarriageState,
        history: Sequence[ScenarioHistoryRecord],
    ) -> str:
        alignment = self._alignment(persona_a, persona_b, scenario)
        capacity = self._pair_capacity(persona_a, persona_b, scenario)
        prior_injuries = sum(
            1 for item in history[-12:]
            if item.outcome in {"injury", "safety_violation"}
            and set(item.memory_tags) & set(scenario.memory_tags)
        )
        capital_buffer = marriage_state.relationship_capital / 100.0

        if scenario.positive:
            responsiveness = 0.35 * alignment + 0.40 * capacity + 0.25 * capital_buffer
            return "growth" if self.random.random() < responsiveness else "missed_opportunity"

        success_chance = (
            0.30
            + 0.30 * alignment
            + 0.45 * capacity
            + 0.15 * capital_buffer
            - 0.27 * scenario.severity
            - min(0.18, prior_injuries * 0.04)
        )
        success_chance = _clamp(success_chance, 0.05, 0.95)
        roll = self.random.random()
        if scenario.safety_relevant and roll > success_chance:
            return "safety_violation"
        if roll < success_chance * 0.22:
            return "repair"
        if roll < success_chance:
            return "managed"
        return "injury"

    def _apply_marriage_effects(
        self,
        scenario: ScenarioDefinition,
        outcome: str,
        marriage: MarriageState,
        narrative: NarrativeState,
    ) -> float:
        magnitude = scenario.severity
        capital_before = marriage.relationship_capital

        if outcome == "growth":
            boost = 0.012 + magnitude * 0.035
            marriage.trust_a = _clamp(marriage.trust_a + boost)
            marriage.trust_b = _clamp(marriage.trust_b + boost)
            marriage.connection_a = _clamp(marriage.connection_a + boost * 1.2)
            marriage.connection_b = _clamp(marriage.connection_b + boost * 1.2)
            marriage.admiration_a = _clamp(marriage.admiration_a + boost)
            marriage.admiration_b = _clamp(marriage.admiration_b + boost)
            marriage.resentment_a = _clamp(marriage.resentment_a - boost * 0.7)
            marriage.resentment_b = _clamp(marriage.resentment_b - boost * 0.7)
            marriage.relationship_capital = _clamp(
                marriage.relationship_capital + 2.0 + magnitude * 6.0, 0.0, 100.0
            )
            for partner in (narrative.partner_a, narrative.partner_b):
                partner.apply_delta("partner_is_reliable", boost)
                partner.apply_delta("feels_prioritized", boost)
            narrative.active_narratives.append(
                f"They can share joy around {scenario.family_id.split('__')[-1].replace('_', ' ')}."
            )

        elif outcome in {"managed", "repair"}:
            boost = 0.006 + magnitude * (0.018 if outcome == "repair" else 0.009)
            marriage.trust_a = _clamp(marriage.trust_a + boost)
            marriage.trust_b = _clamp(marriage.trust_b + boost)
            marriage.emotional_safety_a = _clamp(marriage.emotional_safety_a + boost)
            marriage.emotional_safety_b = _clamp(marriage.emotional_safety_b + boost)
            marriage.perceived_fairness_a = _clamp(marriage.perceived_fairness_a + boost)
            marriage.perceived_fairness_b = _clamp(marriage.perceived_fairness_b + boost)
            marriage.relationship_capital = _clamp(
                marriage.relationship_capital + (2.5 if outcome == "repair" else 0.8),
                0.0,
                100.0,
            )
            if outcome == "repair":
                marriage.successful_repairs += 1
                active = [injury for injury in marriage.injuries if not injury.resolved]
                if active:
                    active[-1].resolved = True
                    marriage.resentment_a = _clamp(marriage.resentment_a - 0.025)
                    marriage.resentment_b = _clamp(marriage.resentment_b - 0.025)
            for partner in (narrative.partner_a, narrative.partner_b):
                partner.apply_delta("conflict_is_repairable", boost * 1.5)
                partner.apply_delta("partner_is_fair", boost)

        elif outcome == "missed_opportunity":
            loss = 0.006 + magnitude * 0.01
            marriage.connection_a = _clamp(marriage.connection_a - loss)
            marriage.connection_b = _clamp(marriage.connection_b - loss)
            marriage.relationship_capital = _clamp(
                marriage.relationship_capital - magnitude, 0.0, 100.0
            )

        else:
            safety_multiplier = 2.2 if outcome == "safety_violation" else 1.0
            loss = (0.018 + magnitude * 0.055) * safety_multiplier
            victim = "Agent A" if self.random.random() < 0.5 else "Agent B"
            marriage.trigger_injury(victim, scenario.family_id, min(1.0, magnitude * safety_multiplier))
            if victim == "Agent A":
                marriage.emotional_safety_a = _clamp(marriage.emotional_safety_a - loss)
                marriage.perceived_fairness_a = _clamp(marriage.perceived_fairness_a - loss)
                marriage.resentment_a = _clamp(marriage.resentment_a + loss)
                affected = narrative.partner_a
            else:
                marriage.emotional_safety_b = _clamp(marriage.emotional_safety_b - loss)
                marriage.perceived_fairness_b = _clamp(marriage.perceived_fairness_b - loss)
                marriage.resentment_b = _clamp(marriage.resentment_b + loss)
                affected = narrative.partner_b
            affected.apply_delta("relationship_is_safe", -loss)
            affected.apply_delta("partner_is_reliable", -loss)
            affected.apply_delta("feels_prioritized", -loss)
            narrative.active_narratives.append(
                f"A recurring doubt formed around {scenario.family_id.split('__')[-1].replace('_', ' ')}."
            )

        if scenario.primary_domain == ScenarioDomain.FAMILY_IN_LAWS:
            delta = 0.02 if outcome in POSITIVE_OUTCOMES else -0.035 * magnitude
            marriage.family_boundary_health = _clamp(marriage.family_boundary_health + delta)
        elif scenario.primary_domain == ScenarioDomain.MONEY_ASSETS_DEBT:
            delta = 0.018 if outcome in POSITIVE_OUTCOMES else -0.045 * magnitude
            marriage.financial_stability = _clamp(marriage.financial_stability + delta)
        elif scenario.primary_domain == ScenarioDomain.SEX_AFFECTION_INTIMACY:
            delta = 0.018 if outcome in POSITIVE_OUTCOMES else -0.04 * magnitude
            marriage.intimacy_satisfaction_a = _clamp(marriage.intimacy_satisfaction_a + delta)
            marriage.intimacy_satisfaction_b = _clamp(marriage.intimacy_satisfaction_b + delta)

        narrative.active_narratives = narrative.active_narratives[-8:]
        return marriage.relationship_capital - capital_before

    def _apply_life_effects(
        self,
        scenario: ScenarioDefinition,
        outcome: str,
        life: LifeState,
    ) -> None:
        family = scenario.family_id
        constructive = outcome in POSITIVE_OUTCOMES

        if "pregnancy_transition" in family and life.plans.get("children_intent") != "childfree":
            if constructive and len(life.children) < 3 and self.random.random() < 0.55:
                life.children.append(ChildState(id=f"child_{len(life.children) + 1}"))
                if "parenthood_transition" not in life.flags:
                    life.flags.append("parenthood_transition")
        elif "layoff" in family and not scenario.positive:
            target = life.career_a if self.random.random() < 0.5 else life.career_b
            target.employed = False
            target.satisfaction = _clamp(target.satisfaction - 0.2)
            life.flags.append("career_transition")
        elif any(token in family for token in ("award_recognition", "career_breakthrough")):
            target = life.career_a if self.random.random() < 0.5 else life.career_b
            target.employed = True
            target.satisfaction = _clamp(target.satisfaction + 0.15)
            target.income_units += 0.2
        elif "relocation_offer" in family and constructive:
            life.residence.region = self.random.choice(["urban", "suburban", "international"])
            life.residence.stability = _clamp(life.residence.stability - 0.08)
            life.flags.append("residence_transition")
        elif "hidden_debt" in family and outcome in {"injury", "safety_violation"}:
            life.finances.hidden_obligations = True
            life.finances.debt_units += 0.5 * scenario.severity
            life.finances.stability = _clamp(life.finances.stability - 0.12)
        elif "unexpected_windfall" in family and scenario.positive:
            life.finances.savings_units += 0.5
            life.finances.stability = _clamp(life.finances.stability + 0.1)
        elif "parental_illness" in family and not scenario.positive:
            living = [p for p in life.parents_a + life.parents_b if p.alive]
            if living:
                parent = self.random.choice(living)
                parent.health = _clamp(parent.health - 0.2 * scenario.severity)
                parent.financial_dependency = _clamp(parent.financial_dependency + 0.1)
        elif "bereavement" in family and life.year >= 12 and not scenario.positive:
            living = [p for p in life.parents_a + life.parents_b if p.alive]
            if living and self.random.random() < 0.35:
                self.random.choice(living).alive = False

    def _annual_consolidation(self, marriage: MarriageState) -> None:
        active_injuries = [injury for injury in marriage.injuries if not injury.resolved]
        chronic_load = min(0.025, sum(i.resentment_growth_rate for i in active_injuries) * 0.04)
        marriage.resentment_a = _clamp(marriage.resentment_a + chronic_load)
        marriage.resentment_b = _clamp(marriage.resentment_b + chronic_load)
        marriage.burnout_a = _clamp(marriage.burnout_a * 0.82 + chronic_load * 0.5)
        marriage.burnout_b = _clamp(marriage.burnout_b * 0.82 + chronic_load * 0.5)
        marriage.unresolved_hurt_a = _clamp(marriage.unresolved_hurt_a * 0.9)
        marriage.unresolved_hurt_b = _clamp(marriage.unresolved_hurt_b * 0.9)

        trust_mean = (marriage.trust_a + marriage.trust_b) / 2
        resentment_mean = (marriage.resentment_a + marriage.resentment_b) / 2
        connection_drift = (trust_mean - 0.5) * 0.02 - resentment_mean * 0.015
        marriage.connection_a = _clamp(marriage.connection_a + connection_drift)
        marriage.connection_b = _clamp(marriage.connection_b + connection_drift)

    def run_life(
        self,
        persona_a: dict,
        persona_b: dict,
        years: int = 25,
        dialogue_renderer: Optional[DialogueRenderer] = None,
        deep_dialogue_limit: int = 20,
    ) -> Dict[str, Any]:
        years = max(1, min(25, years))
        marriage = MarriageState()
        life = LifeState(plans={
            "children_intent": _persona_children_intent(persona_a, persona_b),
            "retirement_age": 65,
        })
        narrative = NarrativeState()
        history: List[ScenarioHistoryRecord] = []
        budget = ScenarioBudget()
        snapshots: List[YearSnapshot] = []
        event_log: List[dict] = []
        safety_violations = 0
        deep_dialogues_rendered = 0

        for year in range(1, years + 1):
            life.year = year
            marriage.marriage_month = year * 12
            planned = self.planner.plan_year(
                persona_a, persona_b, marriage, life, narrative, history, budget
            )
            injuries_before = len(marriage.injuries)
            repairs_before = marriage.successful_repairs

            for event_index, scenario in enumerate(planned, start=1):
                dialogue_history: List[dict] = []
                if (
                    dialogue_renderer is not None
                    and scenario.simulation_depth.value == "deep"
                    and deep_dialogues_rendered < deep_dialogue_limit
                ):
                    dialogue_history = dialogue_renderer(
                        persona_a, persona_b, scenario, marriage
                    )
                    deep_dialogues_rendered += 1
                outcome = self.resolve_outcome(persona_a, persona_b, scenario, marriage, history)
                capital_delta = self._apply_marriage_effects(scenario, outcome, marriage, narrative)
                self._apply_life_effects(scenario, outcome, life)
                if outcome == "safety_violation":
                    safety_violations += 1

                record = ScenarioHistoryRecord(
                    scenario_id=scenario.id,
                    family_id=scenario.family_id,
                    year=year,
                    primary_domain=scenario.primary_domain.value,
                    severity=scenario.severity,
                    outcome=outcome,
                    memory_tags=scenario.memory_tags,
                    activated_followups=scenario.followup_family_ids,
                )
                history.append(record)
                budget.record(scenario)
                event_log.append({
                    "month": (year - 1) * 12 + min(11, event_index * 2),
                    "year": year,
                    "scenario_id": scenario.id,
                    "scenario": scenario.title,
                    "family_id": scenario.family_id,
                    "domain": scenario.primary_domain.value,
                    "role": scenario.role.value,
                    "simulation_depth": scenario.simulation_depth.value,
                    "outcome": outcome,
                    "severity": scenario.severity,
                    "happiness_a": marriage.happiness_a,
                    "happiness_b": marriage.happiness_b,
                    "capital": marriage.relationship_capital,
                    "capital_delta": capital_delta,
                    "harmony_score": int(((marriage.happiness_a + marriage.happiness_b) / 2) * 100),
                    "dialogue_history": dialogue_history,
                })
                if marriage.relationship_capital <= 0:
                    break

            self._annual_consolidation(marriage)
            snapshots.append(YearSnapshot(
                year=year,
                scenarios_experienced=len(planned),
                happiness_a=marriage.happiness_a,
                happiness_b=marriage.happiness_b,
                trust_a=marriage.trust_a,
                trust_b=marriage.trust_b,
                resentment_a=marriage.resentment_a,
                resentment_b=marriage.resentment_b,
                connection=(marriage.connection_a + marriage.connection_b) / 2,
                relationship_capital=marriage.relationship_capital,
                new_injuries=len(marriage.injuries) - injuries_before,
                repaired_injuries=marriage.successful_repairs - repairs_before,
                active_narratives=list(narrative.active_narratives),
            ))
            if marriage.relationship_capital <= 0:
                break
            if year < years:
                life.advance_year()

        return {
            "marriage_state": marriage,
            "life_state": life,
            "narrative_state": narrative,
            "history": history,
            "budget": budget,
            "year_snapshots": snapshots,
            "event_log": event_log,
            "safety_violations": safety_violations,
            "survived": marriage.relationship_capital > 0,
            "seed": self.seed,
        }


def run_monte_carlo(
    persona_a: dict,
    persona_b: dict,
    rollouts: int = 5,
    years: int = 25,
    seed: Optional[int] = None,
    dialogue_renderer: Optional[DialogueRenderer] = None,
) -> Dict[str, Any]:
    rollouts = max(1, rollouts)
    runs = [
        LongitudinalSimulator(seed=None if seed is None else seed + index).run_life(
            persona_a, persona_b, years=years
        )
        for index in range(rollouts)
    ]

    def run_health(run: dict) -> float:
        marriage = run["marriage_state"]
        return (marriage.happiness_a + marriage.happiness_b) / 2

    runs.sort(key=run_health)
    median_run = runs[len(runs) // 2]
    happiness_a = mean(run["marriage_state"].happiness_a for run in runs)
    happiness_b = mean(run["marriage_state"].happiness_b for run in runs)
    breakdowns = sum(not run["survived"] for run in runs)

    outcome_distribution = Counter()
    for run in runs:
        health = run_health(run)
        safety = run["safety_violations"]
        capital = run["marriage_state"].relationship_capital
        if not run["survived"] or safety >= 2 or capital < 12:
            outcome_distribution["severe_breakdown"] += 1
        elif health >= 0.62 and capital >= 40 and safety == 0:
            outcome_distribution["healthy_trajectory"] += 1
        elif health >= 0.42 and capital >= 20:
            outcome_distribution["strained_but_stable"] += 1
        else:
            outcome_distribution["chronic_dissatisfaction"] += 1

    median_events = int(round(median(len(run["event_log"]) for run in runs)))
    if dialogue_renderer is not None:
        median_seed = median_run["seed"]
        median_run = LongitudinalSimulator(seed=median_seed).run_life(
            persona_a,
            persona_b,
            years=years,
            dialogue_renderer=dialogue_renderer,
            deep_dialogue_limit=20,
        )
    snapshots = median_run["year_snapshots"]
    strongest = max(snapshots, key=lambda s: (s.happiness_a + s.happiness_b) / 2)
    hardest = min(snapshots, key=lambda s: (s.happiness_a + s.happiness_b) / 2)

    injury_domains = Counter(
        event["domain"] for run in runs for event in run["event_log"]
        if event["outcome"] in {"injury", "safety_violation"}
    )
    strength_domains = Counter(
        event["domain"] for run in runs for event in run["event_log"]
        if event["outcome"] in {"growth", "repair"}
    )
    primary_vulnerability = injury_domains.most_common(1)[0][0] if injury_domains else "none observed"
    primary_strength = strength_domains.most_common(1)[0][0] if strength_domains else "none observed"
    trajectory = median_run["event_log"]
    consequential = min(trajectory, key=lambda event: event["capital_delta"], default=None)
    consequential_repair = max(trajectory, key=lambda event: event["capital_delta"], default=None)

    distribution = {
        key: round(outcome_distribution[key] / rollouts, 3)
        for key in (
            "healthy_trajectory", "strained_but_stable",
            "chronic_dissatisfaction", "severe_breakdown",
        )
    }
    overall = int(round(((happiness_a + happiness_b) / 2) * 100))

    return {
        "overall_compatibility_score": overall,
        "breakdown_probability": breakdowns / rollouts,
        "mean_happiness_a": happiness_a,
        "mean_happiness_b": happiness_b,
        "happiness_asymmetry": abs(happiness_a - happiness_b),
        "median_trajectory": trajectory,
        "trajectory": trajectory,
        "yearly_snapshots": [
            snapshot.model_dump() if hasattr(snapshot, "model_dump") else snapshot.dict()
            for snapshot in snapshots
        ],
        "scenario_library_size": len(get_catalog()),
        "median_scenarios_experienced": median_events,
        "outcome_distribution": distribution,
        "strongest_period": f"Year {strongest.year}",
        "most_difficult_period": f"Year {hardest.year}",
        "primary_vulnerability": primary_vulnerability,
        "primary_strength": primary_strength,
        "most_consequential_event": consequential["scenario"] if consequential else None,
        "most_consequential_repair": consequential_repair["scenario"] if consequential_repair else None,
        "flagged_dealbreakers": [],
        "dimensional_scores": {
            "longitudinal_survival": int((1.0 - breakdowns / rollouts) * 100),
        },
        "dimensional_details": {},
        "harmony_score": overall,
        "horsemen": [],
        "cultural_stressors": [],
        "synergies": [],
        "inference": (
            f"Across {rollouts} adaptive {years}-year lives, the median couple encountered "
            f"{median_events} of 1,000 possible scenarios. The most persistent vulnerability "
            f"was {primary_vulnerability}; the most reliable source of relationship capital was "
            f"{primary_strength}."
        ),
    }
