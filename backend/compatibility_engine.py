import logging
from statistics import mean
from typing import Dict, List, Any, Tuple, Union

from simulation_engine import get_trait, run_simulation
from evaluation_engine import compute_harmony_index
from scenarios import get_scenarios_by_category
from llm_analysis import analyze_text_compatibility
from intake_questions import INTAKE_SECTIONS

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

    # ── Phase 8: HYGIENE, SEXUAL COMPAT, DAILY RITUALS ─────────────────────
    "hygiene_standard":               ("similarity",),   # shared cleanliness expectation
    "body_comfort":                   ("similarity",),   # shared comfort with bodily naturalness
    "sexual_openness":                ("similarity",),   # kink-to-vanilla alignment
    "libido_alignment":               ("balance", 0.50), # desire frequency; gap = resentment
    "intimacy_communication":         ("floor",),        # weakest partner limits sexual dialogue
    "ritual_rigidity":                ("similarity",),   # routine attachment alignment
    "sleep_schedule_compatibility":   ("similarity",),   # early bird vs. night owl
    "personal_space_need":            ("balance", 0.50), # gap = anxious-avoidant activation
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
    "hygiene_standard", "body_comfort",
]

TRUST_TRAITS = [
    "jealousy_threshold", "privacy_need", "couple_first_orientation",
    "boundary_strength", "partner_advocacy",
]

AUTONOMY_TRAITS = [
    "autonomy_need", "egalitarianism", "career_priority",
    "identity_rigidity", "social_image_sensitivity",
    "personal_space_need", "ritual_rigidity",
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
    # Phase 8
    "hygiene_domestic":  "Hygiene & Domestic Habits",
    "intimacy_sexual":   "Intimacy & Sexual Compatibility",
    "daily_rituals":     "Daily Rituals & Cohabitation",
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


# ---------- Timeline Generation ----------

def generate_timeline(all_scenarios: List[dict], years: int = 15) -> List[dict]:
    """Generates an event timeline spanning `years`. Frequency determines probability of inclusion per year."""
    import random
    from state_models import MarriageState, LifePhase
    timeline = []
    
    # Simple hazard function based on frequencies
    freq_probs = {
        "High": 0.8,
        "Medium": 0.4,
        "Low": 0.1,
        "Very low": 0.05
    }
    
    # Temporary mock state just to track time during timeline generation
    mock_state = MarriageState()
    
    for month in range(1, years * 12 + 1):
        mock_state.marriage_month = month
        current_phase = mock_state.current_life_phase
        
        # Pick 1 scenario randomly, but weighted by frequency and life phase
        candidate = random.choice(all_scenarios)
        base_prob = freq_probs.get(candidate.get("frequency", "Medium"), 0.4)
        
        # Apply phase modifiers based on category
        cat = candidate.get("category", "")
        modifier = 1.0
        
        if current_phase == LifePhase.NEWLYWED:
            if cat in ["family_dynamics", "financial"]: modifier = 1.2
            elif cat == "parenting": modifier = 0.1
        elif current_phase == LifePhase.CAREER_BUILDING:
            if cat == "financial": modifier = 1.3
        elif current_phase == LifePhase.CHILDCARE:
            if cat == "parenting": modifier = 1.5
            if cat == "intimacy": modifier = 1.2
        elif current_phase == LifePhase.MIDLIFE:
            if cat == "autonomy_identity": modifier = 1.4
            
        prob = base_prob * modifier
        
        if random.random() < prob:
            # We add it to the timeline
            event = candidate.copy()
            event["month"] = month
            timeline.append(event)
            
    return timeline


# ---------- Multi-scenario compatibility report ----------

def run_full_compatibility_report(
    agent_a: dict,
    agent_b: dict,
    answers_a: dict = None,
    answers_b: dict = None,
    max_turns: int = 4,
) -> Dict[str, Any]:
    import random
    import math
    from state_models import MarriageState
    MONTE_CARLO_N = 5
    SIMULATION_YEARS = 15

    def sample_traits(agent: dict) -> dict:
        sampled = {}
        for trait, dist in agent.get("traits", {}).items():
            mean_val = dist.get("mean", 0.5)
            variance = dist.get("variance", 0.01)
            std_dev = math.sqrt(variance)
            val = random.gauss(mean_val, std_dev)
            sampled[trait] = max(0.0, min(1.0, val))
        return sampled

    all_scenarios = get_scenarios()
    
    # Store results across N Monte Carlo lives
    monte_carlo_results = []

    # Run N full lives
    for mc_idx in range(MONTE_CARLO_N):
        logger.info(f"--- Monte Carlo Rollout {mc_idx + 1}/{MONTE_CARLO_N} ---")
        
        timeline = generate_timeline(all_scenarios, years=SIMULATION_YEARS)
        sampled_a = sample_traits(agent_a)
        sampled_b = sample_traits(agent_b)
        
        m_state = MarriageState()
        
        life_log = []
        for event in timeline:
            m_state.marriage_month = event["month"]
            
            result = run_simulation(
                agent_a, agent_b, 
                sampled_a, sampled_b, 
                event, m_state, 
                max_turns=3
            )
            
            # The run_simulation updates m_state in place
            analysis = compute_harmony_index(result["dialogue_history"])
            
            life_log.append({
                "month": event["month"],
                "scenario": event["title"],
                "happiness_a": m_state.happiness_a,
                "happiness_b": m_state.happiness_b,
                "capital": m_state.relationship_capital,
                "harmony_score": analysis["harmony_score"],
                "dialogue_history": result["dialogue_history"]
            })
            
            if m_state.relationship_capital <= 0:
                logger.warning(f"Marriage breakdown at month {event['month']}")
                break
                
        monte_carlo_results.append({
            "final_happiness_a": m_state.happiness_a,
            "final_happiness_b": m_state.happiness_b,
            "final_capital": m_state.relationship_capital,
            "survived": m_state.relationship_capital > 0,
            "duration_months": m_state.marriage_month,
            "life_log": life_log
        })

    # Aggregate
    survived_count = sum(1 for r in monte_carlo_results if r["survived"])
    avg_happiness_a = sum(r["final_happiness_a"] for r in monte_carlo_results) / MONTE_CARLO_N
    avg_happiness_b = sum(r["final_happiness_b"] for r in monte_carlo_results) / MONTE_CARLO_N
    
    # Find the median run (based on average happiness)
    monte_carlo_results.sort(key=lambda x: (x["final_happiness_a"] + x["final_happiness_b"]) / 2)
    median_run = monte_carlo_results[MONTE_CARLO_N // 2]
    
    overall_compatibility = int(((avg_happiness_a + avg_happiness_b) / 2) * 100)

    # Feature Attribution Logic (Phase 2 V4)
    failure_causes = {}
    for r in monte_carlo_results:
        if not r["survived"] and r["life_log"]:
            # Find the last 2 events before breakdown
            for event in r["life_log"][-2:]:
                scenario_title = event["scenario"]
                failure_causes[scenario_title] = failure_causes.get(scenario_title, 0) + 1
    
    inference_text = f"Relationship survived {survived_count}/{MONTE_CARLO_N} Monte Carlo rollouts spanning 15 years. "
    if survived_count < MONTE_CARLO_N and failure_causes:
        top_cause = max(failure_causes, key=failure_causes.get)
        inference_text += f"In failed timelines, cascading stress was most frequently triggered by events like '{top_cause}'."
    elif survived_count == MONTE_CARLO_N:
        inference_text += "High resilience was observed across all stress tests, indicating strong capital recovery mechanics."

    # We return the median run's trajectory
    return {
        "overall_compatibility_score": overall_compatibility,
        "breakdown_probability": 1.0 - (survived_count / MONTE_CARLO_N),
        "mean_happiness_a": avg_happiness_a,
        "mean_happiness_b": avg_happiness_b,
        "median_trajectory": median_run["life_log"],
        "flagged_dealbreakers": [],
        "dimensional_scores": {"longitudinal_survival": int((survived_count / MONTE_CARLO_N) * 100)},
        "dimensional_details": {},
        "harmony_score": overall_compatibility,
        "horsemen": [],
        "cultural_stressors": [],
        "synergies": [],
        "trajectory": median_run["life_log"],
        "inference": inference_text
    }
