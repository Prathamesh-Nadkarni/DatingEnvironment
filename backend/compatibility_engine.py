import logging
from statistics import mean
from typing import Dict, List, Any, Tuple, Union

from simulation_engine import get_trait, run_simulation
from evaluation_engine import compute_harmony_index
from scenarios import get_scenarios_by_category

logger = logging.getLogger("mirofish.compatibility")

# ---------------------------------------------------------------------------
# Trait scoring models — three fundamental compatibility patterns in
# relationship psychology, plus capacity/risk helpers.
#
# SIMILARITY     — alignment is what matters; divergence always hurts.
#                  Examples: egalitarianism, parenting_alignment, privacy_need.
#                  Two traditional people CAN be happy; two modern people CAN
#                  be happy. What kills a relationship is one of each.
#
# COMPLEMENTARITY — one high + one low creates the healthiest functional pair.
#                   BOTH at the same extreme is the failure mode.
#                   The pair average should be moderate AND the gap should be
#                   meaningful — this is NOT the same as "balance."
#                   Example: conflict_dominance — one who initiates + one who
#                   can yield = healthy disagreements. Two bulldozers = chronic
#                   power struggle. Two avoiders = nothing ever gets resolved.
#
# BALANCE(target) — both-same-extreme in EITHER direction is risky. Pair should
#                   share a moderate level near `target` (default 0.5).
#                   Large divergence between partners also adds friction.
#                   Examples:
#                     risk_tolerance  (target=0.45) — both reckless → chaos;
#                                                      both paralysed → stagnation
#                     withdrawal_tendency (target=0.30) — lower shared withdrawal
#                                                          is healthier for everyone
#                     autonomy_need (target=0.50) — large gap = anxious-avoidant
#                                                    attachment trap
#
# FLOOR          — weakest partner is the real bottleneck. One excellent
#                  repairer can compensate a little but cannot carry the pair.
#                  Examples: repair_skill, co_regulation_capacity, forgiveness.
#
# JOINT_HIGH     — both high is unconditionally better.
#                  Examples: partner_advocacy, boundary_strength.
#
# JOINT_LOW      — both low is unconditionally better (toxicity/risk traits).
#                  Examples: resentment_accumulation_rate, burnout_vulnerability.
# ---------------------------------------------------------------------------

# Spec format: ("model",) or ("balance", target_float)
TraitSpec = Union[Tuple[str], Tuple[str, float]]

TRAIT_MODEL: Dict[str, TraitSpec] = {
    # ── SIMILARITY ──────────────────────────────────────────────────────────
    "egalitarianism":             ("similarity",),
    "tradition_compliance":       ("similarity",),
    "family_deference":           ("similarity",),
    "couple_first_orientation":   ("similarity",),  # fixed: two family-first = compatible
    "parenting_alignment":        ("similarity",),
    "moral_reasoning_style":      ("similarity",),
    "household_order_preference": ("similarity",),
    "privacy_need":               ("similarity",),
    "social_image_sensitivity":   ("similarity",),
    "security_need":              ("similarity",),   # shared saving/spending mindset
    "financial_mutuality":        ("similarity",),

    # ── COMPLEMENTARITY ─────────────────────────────────────────────────────
    # assertive + adaptive = healthy; two bulldozers or two avoiders = broken
    "conflict_dominance":         ("complementarity",),

    # ── BALANCE (with tuned healthy targets) ────────────────────────────────
    "risk_tolerance":    ("balance", 0.45),  # slightly cautious pairs fare better
    "withdrawal_tendency":("balance", 0.30), # lower shared avoidance is healthier
    "career_priority":   ("balance", 0.50),  # neither neglect-relationship nor idle
    "jealousy_threshold":("balance", 0.30),  # low shared jealousy = trust-based bond
    "identity_rigidity": ("balance", 0.30),  # some flexibility is always healthier
    "autonomy_need":     ("balance", 0.50),  # gap triggers anxious-avoidant dynamic

    # ── FLOOR ───────────────────────────────────────────────────────────────
    "repair_skill":           ("floor",),
    "co_regulation_capacity": ("floor",),
    "forgiveness_rate":       ("floor",),
    "distress_tolerance":     ("floor",),

    # ── JOINT_HIGH ──────────────────────────────────────────────────────────
    "partner_advocacy":       ("joint_high",),
    "boundary_strength":      ("joint_high",),
    "caregiving_flexibility": ("joint_high",),

    # ── JOINT_LOW ───────────────────────────────────────────────────────────
    "resentment_accumulation_rate": ("joint_low",),
    "burnout_vulnerability":        ("joint_low",),
    "shame_sensitivity":            ("joint_low",),
    "guilt_susceptibility":         ("joint_low",),
}


def _score_trait(a: float, b: float, spec: TraitSpec) -> float:
    """Score a single trait-pair (0–1) using the model encoded in spec."""
    model = spec[0]

    if model == "similarity":
        return 1.0 - abs(a - b)

    if model == "complementarity":
        # Best when: pair_avg is near 0.5 AND divergence is high.
        # Both aspects matter: the pair needs one of each role (centre) and
        # they need to be meaningfully different (divergence).
        pair_avg = (a + b) / 2.0
        divergence = abs(a - b)
        centre = 1.0 - abs(pair_avg - 0.5) * 2.0   # 1.0 when avg=0.5
        gap = min(divergence / 0.5, 1.0)            # saturates at 0.5 difference
        return 0.35 * centre + 0.65 * gap

    if model == "balance":
        target = spec[1] if len(spec) > 1 else 0.5
        pair_avg = (a + b) / 2.0
        centre_penalty = abs(pair_avg - target) * 2.0    # worst far from target
        diverge_penalty = abs(a - b) * 0.30              # large gap also bad
        return max(0.0, 1.0 - centre_penalty - diverge_penalty)

    if model == "floor":
        return min(1.0, min(a, b) + 0.15 * abs(a - b))

    if model == "joint_high":
        return (a + b) / 2.0

    if model == "joint_low":
        return 1.0 - (a + b) / 2.0

    return 1.0 - abs(a - b)


def _score_trait_pair(prompt_a: str, prompt_b: str, trait: str) -> float:
    a = get_trait(prompt_a, trait)
    b = get_trait(prompt_b, trait)
    spec = TRAIT_MODEL.get(trait, ("similarity",))
    return _score_trait(a, b, spec)


# ---------- Trait groups for sub-scores ----------

VALUE_TRAITS = [
    "egalitarianism", "tradition_compliance", "family_deference",
    "parenting_alignment", "moral_reasoning_style",
]

CONFLICT_TRAITS = [
    "repair_skill", "co_regulation_capacity", "forgiveness_rate",
    "conflict_dominance", "withdrawal_tendency",
]

EMOTIONAL_TRAITS = [
    "co_regulation_capacity", "distress_tolerance", "burnout_vulnerability",
    "shame_sensitivity",
]

PRACTICAL_TRAITS = [
    "financial_mutuality", "risk_tolerance", "security_need",
    "household_order_preference", "career_priority",
]

TRUST_TRAITS = [
    "jealousy_threshold", "privacy_need", "couple_first_orientation",
    "boundary_strength", "partner_advocacy",
]

AUTONOMY_TRAITS = [
    "autonomy_need", "egalitarianism", "career_priority",
    "identity_rigidity", "social_image_sensitivity",
]

DEALBREAKER_THRESHOLD = 25      # must be truly hostile (score <= 25) to flag
MAX_DEALBREAKER_PENALTY = 25    # cap total dealbreaker penalty so one bad category
                                # doesn't obliterate an otherwise real score
SCENARIOS_PER_CATEGORY = 3

TRAIT_WEIGHT = 0.30
SIMULATION_WEIGHT = 0.70

CATEGORY_LABELS = {
    "family_dynamics":   "Family Dynamics",
    "financial":         "Financial Alignment",
    "autonomy_identity": "Autonomy & Identity",
    "parenting":         "Parenting & Commitment",
    "crisis_resilience": "Crisis Resilience",
    "loyalty_trust":     "Loyalty & Trust",
}


# ---------- Static trait compatibility ----------

def compute_trait_compatibility(prompt_a: str, prompt_b: str) -> Dict[str, float]:
    """
    Returns 6 sub-scores (0-1) using model-appropriate scoring per trait.

    Sub-scores:
      values         — core life values alignment (similarity model)
      conflict_style — repair capacity + balance of conflict approach
      emotional      — emotional regulation and resilience
      practical      — financial/household/career balance
      trust          — jealousy, privacy, loyalty, advocacy
      autonomy       — independence, identity, career balance
    """
    def _group_score(traits):
        return mean(_score_trait_pair(prompt_a, prompt_b, t) for t in traits)

    values_score = _group_score(VALUE_TRAITS)
    conflict_score = _group_score(CONFLICT_TRAITS)
    emotional_score = _group_score(EMOTIONAL_TRAITS)
    practical_score = _group_score(PRACTICAL_TRAITS)
    trust_score = _group_score(TRUST_TRAITS)
    autonomy_score = _group_score(AUTONOMY_TRAITS)

    logger.info(
        "  Trait compatibility -> values=%.2f conflict=%.2f emotional=%.2f "
        "practical=%.2f trust=%.2f autonomy=%.2f",
        values_score, conflict_score, emotional_score,
        practical_score, trust_score, autonomy_score,
    )

    return {
        "values": round(values_score, 3),
        "conflict_style": round(conflict_score, 3),
        "emotional": round(emotional_score, 3),
        "practical": round(practical_score, 3),
        "trust": round(trust_score, 3),
        "autonomy": round(autonomy_score, 3),
    }


# ---------- Scenario selection ----------

def _pick_scenarios(category_scenarios: List[dict], n: int) -> List[dict]:
    ranked = sorted(
        category_scenarios,
        key=lambda s: (s.get("weight", 1), s.get("dealbreaker", False)),
        reverse=True,
    )
    return ranked[:n]


# ---------- Multi-scenario compatibility report ----------

def run_full_compatibility_report(
    prompt_a: str,
    prompt_b: str,
    max_turns: int = 4,
) -> Dict[str, Any]:
    logger.info("=" * 70)
    logger.info(
        "COMPATIBILITY REPORT: up to %d scenarios per category (%d categories)",
        SCENARIOS_PER_CATEGORY, len(CATEGORY_LABELS),
    )
    logger.info("=" * 70)

    trait_compat = compute_trait_compatibility(prompt_a, prompt_b)

    by_category = get_scenarios_by_category()
    dimensional_scores: Dict[str, int] = {}
    dimensional_details: Dict[str, List[Dict[str, Any]]] = {}
    flagged_dealbreakers: List[str] = []

    for category in CATEGORY_LABELS:
        cat_scenarios = by_category.get(category, [])
        if not cat_scenarios:
            continue

        picked = _pick_scenarios(cat_scenarios, SCENARIOS_PER_CATEGORY)
        scenario_results: List[Dict[str, Any]] = []
        weighted_sum = 0.0
        weight_total = 0.0

        for scenario in picked:
            w = scenario.get("weight", 1)
            logger.info(
                "  [%s] Running: '%s' (weight=%d, db=%s)",
                category, scenario["title"], w, scenario.get("dealbreaker", False),
            )
            sim_result = run_simulation(prompt_a, prompt_b, scenario, max_turns=max_turns)
            analysis = compute_harmony_index(sim_result["dialogue_history"])

            score = analysis["harmony_score"]
            weighted_sum += score * w
            weight_total += w

            detail = {
                "scenario_id": scenario["id"],
                "scenario_title": scenario["title"],
                "harmony_score": score,
                "trajectory": analysis["trajectory"],
                "inference": analysis.get("inference", ""),
                "weight": w,
                "dealbreaker": scenario.get("dealbreaker", False),
            }
            scenario_results.append(detail)

            if scenario.get("dealbreaker") and score <= DEALBREAKER_THRESHOLD:
                flagged_dealbreakers.append(scenario["id"])
                logger.info(
                    "  *** DEALBREAKER FLAGGED: %s scored %d (threshold %d) ***",
                    scenario["id"], score, DEALBREAKER_THRESHOLD,
                )

        cat_score = int(weighted_sum / weight_total) if weight_total > 0 else 50
        dimensional_scores[category] = cat_score
        dimensional_details[category] = scenario_results

    trait_avg = mean(trait_compat.values())
    sim_avg = mean(dimensional_scores.values()) if dimensional_scores else 50.0
    raw_overall = TRAIT_WEIGHT * (trait_avg * 100) + SIMULATION_WEIGHT * sim_avg

    # Each dealbreaker scenario that hits the threshold costs 8 points,
    # but the total is capped so multiple dealbreakers in the same category
    # don't multiply to an absurd penalty.
    dealbreaker_penalty = min(MAX_DEALBREAKER_PENALTY, len(flagged_dealbreakers) * 8)
    overall_score = max(0, min(100, int(raw_overall - dealbreaker_penalty)))

    top_friction_axis = min(dimensional_scores, key=dimensional_scores.get)
    top_strength_axis = max(dimensional_scores, key=dimensional_scores.get)

    verdict = _build_verdict(
        overall_score, trait_compat, dimensional_scores,
        flagged_dealbreakers, top_friction_axis, top_strength_axis,
    )

    logger.info("  OVERALL COMPATIBILITY: %d/100", overall_score)
    logger.info(
        "  Trait avg: %.2f | Sim avg: %.1f | Dealbreaker penalty: -%d",
        trait_avg, sim_avg, dealbreaker_penalty,
    )
    logger.info("  Top friction: %s (%d)", top_friction_axis, dimensional_scores[top_friction_axis])
    logger.info("  Top strength: %s (%d)", top_strength_axis, dimensional_scores[top_strength_axis])
    logger.info("  VERDICT: %s", verdict)
    logger.info("=" * 70)

    return {
        "overall_score": overall_score,
        "trait_compatibility": trait_compat,
        "dimensional_scores": dimensional_scores,
        "dimensional_details": dimensional_details,
        "dealbreakers": flagged_dealbreakers,
        "top_friction_axis": top_friction_axis,
        "top_strength_axis": top_strength_axis,
        "verdict": verdict,
    }


def _build_verdict(
    overall: int,
    trait_compat: Dict[str, float],
    dimensional: Dict[str, int],
    dealbreakers: List[str],
    friction_axis: str,
    strength_axis: str,
) -> str:
    friction_label = CATEGORY_LABELS.get(friction_axis, friction_axis)
    strength_label = CATEGORY_LABELS.get(strength_axis, strength_axis)

    if dealbreakers:
        return (
            f"Fundamental incompatibility detected in {len(dealbreakers)} dealbreaker scenario(s) "
            f"({', '.join(dealbreakers)}). Core values misalignment will compound over time."
        )

    if overall >= 80:
        return (
            f"Highly compatible ({overall}/100) — strong alignment across traits "
            f"(values={trait_compat['values']:.0%}, trust={trait_compat['trust']:.0%}) "
            f"with {strength_label} as the clearest strength."
        )
    elif overall >= 65:
        friction_score = dimensional[friction_axis]
        return (
            f"Compatible ({overall}/100) — solid foundation with room to grow. "
            f"{strength_label} is a key strength; {friction_label} (score {friction_score}) "
            f"requires proactive communication."
        )
    elif overall >= 50:
        return (
            f"Conditionally compatible ({overall}/100) — significant differences in "
            f"{friction_label} will create recurring friction. "
            f"Conflict style compatibility ({trait_compat['conflict_style']:.0%}) and "
            f"trust alignment ({trait_compat['trust']:.0%}) determine if these can be navigated."
        )
    else:
        return (
            f"Low compatibility ({overall}/100) — deep misalignments in {friction_label} and "
            f"values ({trait_compat['values']:.0%} alignment) make sustained harmony unlikely "
            f"without major negotiation on core expectations."
        )
