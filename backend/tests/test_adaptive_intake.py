import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adaptive_router import AdaptiveIntakeState, AdaptiveQuestionRouter


def test_core_screen_is_broad_and_starts_deterministically():
    router = AdaptiveQuestionRouter(seed=7)
    state = AdaptiveIntakeState()
    first = router.select_next(state)
    assert len(router.core_question_ids) == 72
    assert first["id"] == router.core_question_ids[0]
    core_domains = {router.get_question_by_id(question_id)["domain"] for question_id in router.core_question_ids}
    represented_domains = {
        question["domain"] for question in router.question_bank
        if not question["id"].startswith("AR.")
    }
    assert core_domains == represented_domains


def test_structured_evidence_uses_mapping_and_tracks_state():
    router = AdaptiveQuestionRouter(seed=1)
    state = AdaptiveIntakeState()
    router.update_state(state, "4.4", "couple")
    assert state.question_count == 1
    assert state.domain_counts["in_laws_extended_family"] == 1
    assert state.trait_distributions["boundary_strength"]["evidence_count"] == 1
    assert state.trait_distributions["boundary_strength"]["mean"] > 0.5


def test_adaptive_selector_rotates_away_from_recent_domain():
    router = AdaptiveQuestionRouter(seed=3)
    state = AdaptiveIntakeState()
    for question_id in router.core_question_ids:
        question = router.get_question_by_id(question_id)
        if question["domain"] == "in_laws_extended_family":
            router.update_state(state, question_id, "couple")
            if state.domain_counts["in_laws_extended_family"] >= 3:
                break
    state.screen_count = len(router.core_question_ids)
    next_question = router.select_next(state)
    assert next_question is not None
    assert next_question["domain"] != "in_laws_extended_family"


def test_model_evidence_is_constrained_to_canonical_traits():
    router = AdaptiveQuestionRouter(seed=2)
    state = AdaptiveIntakeState()
    router.update_state(state, "4.4", "couple")
    router.add_model_evidence(state, "4.4", [
        {"trait": "boundary_strength", "value": 0.8},
        {"trait": "invented_trait", "value": 0.9},
        {"trait": "partner_advocacy", "value": 1.2},
    ], confidence=0.9)
    traits = {entry["trait"] for entry in state.evidence}
    assert "boundary_strength" in traits
    assert "invented_trait" not in traits
    assert "partner_advocacy" not in traits


def test_stop_requires_minimum_and_can_honor_hard_cap():
    router = AdaptiveQuestionRouter(seed=1)
    state = AdaptiveIntakeState(question_count=149)
    assert not router.should_stop(state)
    state.question_count = 250
    assert router.should_stop(state)
