import os
import sys
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from longitudinal_simulation import LongitudinalSimulator, run_monte_carlo
from scenario_catalog import get_catalog
from scenario_ontology import DOMAIN_ALLOCATIONS, ScenarioDomain
from scenario_planner import AnnualScenarioPlanner, ScenarioBudget, scenario_is_eligible
from state_models import (
    LifeState,
    MarriageState,
    NarrativeState,
    ScenarioHistoryRecord,
)


def persona(level=0.6, children_intent="open"):
    traits = {
        trait: {"mean": level, "variance": 0.02, "confidence": 0.8}
        for trait in {
            "repair_skill", "co_regulation_capacity", "distress_tolerance",
            "family_deference", "partner_advocacy", "boundary_strength",
            "financial_mutuality", "risk_tolerance", "security_need",
            "career_priority", "autonomy_need", "caregiving_flexibility",
            "parenting_alignment", "egalitarianism", "conflict_dominance",
            "withdrawal_tendency", "privacy_need", "jealousy_threshold",
            "sexual_openness", "libido_alignment", "intimacy_communication",
            "tradition_compliance", "identity_rigidity", "household_order_preference",
            "personal_space_need",
        }
    }
    return {"traits": traits, "life_plans": {"children_intent": children_intent}}


def test_catalog_has_locked_allocation_and_positive_share():
    catalog = get_catalog()
    assert len(catalog) == 1000
    assert len({scenario.id for scenario in catalog}) == 1000
    assert len({scenario.family_id for scenario in catalog}) == 120
    assert sum(scenario.positive for scenario in catalog) == 200
    assert Counter(s.primary_domain for s in catalog) == Counter(DOMAIN_ALLOCATIONS)


def test_hard_eligibility_prevents_impossible_child_and_parent_events():
    catalog = get_catalog()
    child_event = next(
        scenario for scenario in catalog
        if "school_choice" in scenario.family_id and not scenario.positive
    )
    parent_event = next(
        scenario for scenario in catalog
        if scenario.eligibility.get("any_parent_alive")
    )
    life = LifeState(year=10)
    assert not scenario_is_eligible(child_event, life)

    for parent in life.parents_a + life.parents_b:
        parent.alive = False
    assert not scenario_is_eligible(parent_event, life)


def test_childfree_plan_filters_inapplicable_parenting_scenarios():
    life = LifeState(year=8, plans={"children_intent": "childfree"})
    eligible_parenting = [
        scenario for scenario in get_catalog()
        if scenario.primary_domain == ScenarioDomain.PARENTING_FERTILITY
        and scenario_is_eligible(scenario, life)
    ]
    assert eligible_parenting
    assert all("children_decision" in scenario.family_id for scenario in eligible_parenting)


def test_causal_activation_increases_followup_weight():
    catalog = get_catalog()
    source = catalog[0]
    followup_family = source.followup_family_ids[0]
    target = next(scenario for scenario in catalog if scenario.family_id == followup_family)
    planner = AnnualScenarioPlanner(catalog, seed=1)
    life = LifeState(year=max(target.min_year, 5))
    budget = ScenarioBudget()
    a, b = persona(0.55), persona(0.65)

    without_history = planner.score_scenario(target, a, b, life, [], budget)
    history = [ScenarioHistoryRecord(
        scenario_id=source.id,
        family_id=source.family_id,
        year=life.year - 1,
        primary_domain=source.primary_domain.value,
        severity=source.severity,
        outcome="injury",
        memory_tags=source.memory_tags,
        activated_followups=source.followup_family_ids,
    )]
    with_history = planner.score_scenario(target, a, b, life, history, budget)
    assert with_history.history_activation > without_history.history_activation
    assert with_history.final_weight > without_history.final_weight


def test_seeded_life_is_reproducible_and_respects_budget():
    a, b = persona(0.72), persona(0.68)
    first = LongitudinalSimulator(seed=42).run_life(a, b)
    second = LongitudinalSimulator(seed=42).run_life(a, b)
    first_ids = [event["scenario_id"] for event in first["event_log"]]
    second_ids = [event["scenario_id"] for event in second["event_log"]]
    assert first_ids == second_ids
    assert 50 <= len(first_ids) <= 150
    assert len(first["year_snapshots"]) == 25


def test_all_persistent_relationship_values_remain_bounded():
    run = LongitudinalSimulator(seed=9).run_life(persona(0.25), persona(0.8))
    marriage = run["marriage_state"]
    bounded = [
        marriage.trust_a, marriage.trust_b,
        marriage.emotional_safety_a, marriage.emotional_safety_b,
        marriage.connection_a, marriage.connection_b,
        marriage.resentment_a, marriage.resentment_b,
        marriage.burnout_a, marriage.burnout_b,
        marriage.happiness_a, marriage.happiness_b,
    ]
    assert all(0.0 <= value <= 1.0 for value in bounded)
    assert 0.0 <= marriage.relationship_capital <= 100.0


def test_monte_carlo_report_exposes_25_year_causal_summary():
    report = run_monte_carlo(persona(0.7), persona(0.65), rollouts=2, seed=11)
    assert report["scenario_library_size"] == 1000
    assert 50 <= report["median_scenarios_experienced"] <= 150
    assert len(report["yearly_snapshots"]) == 25
    assert set(report["outcome_distribution"]) == {
        "healthy_trajectory", "strained_but_stable",
        "chronic_dissatisfaction", "severe_breakdown",
    }
    assert "adaptive 25-year lives" in report["inference"]

