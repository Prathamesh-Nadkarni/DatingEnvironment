import re
import json
import logging
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

logger = logging.getLogger("mirofish.simulation")


class SimulationState(TypedDict):
    agent_a_prompt: str
    agent_b_prompt: str
    scenario_details: dict
    dialogue_history: List[Dict[str, Any]]
    turn_count: int
    max_turns: int
    current_speaker: str
    tension_level: float
    last_category_a: str
    last_category_b: str
    scenario_category: str
    accumulated_stress: float
    relationship_limit: float
    happiness_factor: float


def get_trait(prompt: str, trait: str) -> float:
    try:
        match = re.search(rf'"{trait}":\s*([0-9eE.+-]+)', prompt)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return 0.5


# ---------- Behavioral profile computation ----------

BEHAVIORAL_COMPONENTS = {
    "assertiveness": [
        ("conflict_dominance", 0.25), ("autonomy_need", 0.25),
        ("boundary_strength", 0.25), ("egalitarianism", 0.25),
    ],
    "avoidance": [
        ("withdrawal_tendency", 0.4), ("public_harmony_preference", 0.3),
        ("shame_sensitivity", 0.3),
    ],
    "repair": [
        ("repair_skill", 0.3), ("co_regulation_capacity", 0.3),
        ("forgiveness_rate", 0.2), ("distress_tolerance", 0.2),
    ],
    "deference": [
        ("family_deference", 0.4), ("tradition_compliance", 0.3),
        ("guilt_susceptibility", 0.3),
    ],
}

KEY_TRAITS = [
    "family_deference", "egalitarianism", "boundary_strength",
    "autonomy_need", "tradition_compliance", "couple_first_orientation",
    "withdrawal_tendency", "conflict_dominance", "co_regulation_capacity",
    "repair_skill", "public_harmony_preference", "partner_advocacy",
    "shame_sensitivity", "security_need", "risk_tolerance",
    "jealousy_threshold", "privacy_need", "financial_mutuality",
    "parenting_alignment", "caregiving_flexibility", "household_order_preference",
    "resentment_accumulation_rate", "social_image_sensitivity",
]


def compute_behavioral_profile(prompt: str) -> Dict[str, float]:
    return {
        behavior: sum(get_trait(prompt, t) * w for t, w in components)
        for behavior, components in BEHAVIORAL_COMPONENTS.items()
    }


def compute_trait_distance(prompt_a: str, prompt_b: str) -> float:
    diffs = [abs(get_trait(prompt_a, t) - get_trait(prompt_b, t)) for t in KEY_TRAITS]
    return sum(diffs) / len(diffs)


def find_dominant_clash(own_prompt: str, other_prompt: str) -> str:
    clashes = {
        "fairness": abs(
            get_trait(own_prompt, "egalitarianism")
            - get_trait(other_prompt, "egalitarianism")
        ),
        "family": abs(
            get_trait(own_prompt, "family_deference")
            - get_trait(other_prompt, "couple_first_orientation")
        ),
        "autonomy": abs(
            get_trait(own_prompt, "autonomy_need")
            - get_trait(other_prompt, "tradition_compliance")
        ),
        "conflict_style": abs(
            get_trait(own_prompt, "conflict_dominance")
            - get_trait(other_prompt, "withdrawal_tendency")
        ),
    }
    return max(clashes, key=clashes.get)


# ---------- Message template pools ----------
# Each entry: (internal_thought, spoken_message)

MESSAGES = {
    "compromise": [
        (
            "I need to find middle ground here. Neither of us is entirely wrong.",
            "I hear you, and I understand this is important to you. "
            "Let's try to find a compromise that works for both of us.",
        ),
        (
            "We can get through this if we both give a little. I want us to be a team.",
            "What if we try a middle path? I'm willing to adjust if you can meet me halfway. "
            "Let's work through this together.",
        ),
        (
            "This is hard, but I think we can figure it out together if we stay calm.",
            "I appreciate you sharing how you feel. I understand this is difficult. "
            "Can we brainstorm a solution that respects both our needs?",
        ),
        (
            "I don't want this to become a fight. We're on the same team here.",
            "I know we see this differently, but I respect your perspective. "
            "Can we find a compromise together?",
        ),
    ],
    "assert": [
        (
            "I feel strongly about this and I need to make my position clear.",
            "I understand your perspective, but I need you to understand mine too. "
            "This matters to me deeply and I can't just let it go.",
        ),
        (
            "I can't just accept this. My values are at stake here.",
            "I've thought about this carefully, and I need to be honest "
            "— I don't agree with that approach. We need a different path.",
        ),
        (
            "I have to stand my ground on this. It's about what's right.",
            "Look, I care about your feelings, but what about my needs? "
            "We need to consider what's actually fair here.",
        ),
        (
            "I won't back down on this point. It matters too much to who I am.",
            "I need to push back here. This isn't just a preference "
            "— it's about our fundamental values as a couple.",
        ),
    ],
    "defer": [
        (
            "I must maintain harmony with my family, even if it creates tension between us.",
            "We should respect the elders' wishes on this. "
            "They have more experience and they mean well.",
        ),
        (
            "Family duty weighs heavily on me. I can't just ignore their expectations.",
            "I know it's hard, but we have to adjust for the elders. "
            "Keeping peace with family matters in the long run.",
        ),
        (
            "I feel torn between my partner and my family, but tradition gives me direction.",
            "My parents have sacrificed so much for us. "
            "We must show them respect, even if it means adjusting our plans.",
        ),
        (
            "Going against family feels wrong, even when part of me knows I should stand up.",
            "Let's just do what the elders expect for now. "
            "It isn't worth creating a permanent rift over this.",
        ),
    ],
    "repair": [
        (
            "I can see this is hurting us both. I need to step back and reconnect.",
            "I'm sorry if I came across too strong earlier. "
            "I hear you, and I want us to work through this together.",
        ),
        (
            "The tension between us is more important than being right.",
            "Can we pause for a moment? I understand your frustration, "
            "and I don't want us to keep hurting each other.",
        ),
        (
            "I realize I haven't been listening well enough. I want to understand.",
            "I think we both have valid points. I'm sorry for the tension. "
            "What matters most is that we're a team.",
        ),
        (
            "I don't want to win this argument. I want us both to feel heard.",
            "Let me understand your side better. "
            "I care more about us than about being right on this.",
        ),
    ],
    "withdraw": [
        (
            "I can't handle this tension anymore. I need to shut down and protect myself.",
            "Fine. Do whatever you want. I have nothing more to say about this.",
        ),
        (
            "I'm exhausted by this conversation. I'm checking out emotionally.",
            "I just can't do this right now. Let's just drop it.",
        ),
        (
            "Every word makes it worse. Silence feels safer than speaking.",
            "...",
        ),
        (
            "I feel overwhelmed and invisible in this conversation.",
            "I have nothing more to say. You've clearly made up your mind.",
        ),
    ],
    "escalate": [
        (
            "I'm furious. They never consider my feelings. This pattern is unbearable.",
            "You ALWAYS put everyone else before us! "
            "It's like my feelings never matter to you.",
        ),
        (
            "I feel disgust building. They refuse to see how unfair this is.",
            "This is DISGUSTING. You never stand up for what's right. "
            "You always take the easy path at my expense.",
        ),
        (
            "They're being completely unreasonable and I've lost all patience.",
            "You NEVER listen! Every time this comes up, you shut me down. "
            "I'm sick of it.",
        ),
        (
            "I feel contempt building. They keep choosing the coward's way out.",
            "You always do this — you always choose them over me. "
            "It's not my fault you can't set boundaries.",
        ),
    ],
}

MESSAGES["strained"] = [
    (
        "I'm trying to compromise but this keeps coming back. Resentment is building inside me.",
        "I hear you, and I want to find a solution. "
        "But honestly, I feel like I'm always the one adjusting. That's not fair.",
    ),
    (
        "I want to be reasonable but every time we discuss this, I feel more frustrated.",
        "Let's try to work through this. "
        "But I need you to know — I can't keep compromising every time while nothing changes.",
    ),
    (
        "I'm exhausted from trying to meet in the middle when the middle keeps shifting.",
        "I understand your position, but I'm starting to feel like my needs never get priority. "
        "Something has to change.",
    ),
    (
        "Part of me wants to keep the peace, but another part is done being the flexible one.",
        "Can we please find a real solution? "
        "Because these compromises always seem to go one way, and it's wearing me down.",
    ),
]

CLASH_MODIFIERS = {
    "fairness": {
        "assert": " This is about basic fairness and equality in our relationship.",
        "escalate": " The unfairness of this situation is what makes it unbearable.",
        "defer": " Sometimes tradition and fairness don't align, and that's painful for me.",
    },
    "family": {
        "assert": " We need to set clear boundaries with family.",
        "defer": " Family bonds are sacred and we should honor them.",
        "escalate": " Your family's expectations are destroying our relationship.",
    },
    "autonomy": {
        "assert": " I need my independence respected in this relationship.",
        "defer": " Sometimes we have to put community expectations above personal freedom.",
        "escalate": " I feel completely controlled and suffocated by these expectations.",
    },
    "conflict_style": {
        "assert": " We need to actually talk about this, not just avoid it.",
        "withdraw": " I can't engage when it feels like an attack.",
        "repair": " I think we just approach this differently — not necessarily disagreeing.",
    },
}


# ---------- Scenario-aware dynamics ----------

# Traits most diagnostic for each scenario category — used to compute focused tension
SCENARIO_TRAIT_FOCUS = {
    "family_dynamics":   ["family_deference", "couple_first_orientation", "partner_advocacy", "household_order_preference"],
    "financial":         ["financial_mutuality", "risk_tolerance", "security_need"],
    "autonomy_identity": ["autonomy_need", "tradition_compliance", "egalitarianism", "privacy_need"],
    "parenting":         ["parenting_alignment", "caregiving_flexibility", "identity_rigidity"],
    "crisis_resilience": ["distress_tolerance", "co_regulation_capacity", "repair_skill", "resentment_accumulation_rate"],
    "loyalty_trust":     ["jealousy_threshold", "couple_first_orientation", "boundary_strength", "privacy_need"],
}

# Per-category score boosts for relevant response types
SCENARIO_CATEGORY_BIAS = {
    "family_dynamics":   {"defer": 0.12, "assert": 0.08},
    "financial":         {"assert": 0.10, "compromise": 0.08},
    "autonomy_identity": {"assert": 0.15, "escalate": 0.05},
    "parenting":         {"assert": 0.10, "repair": 0.08},
    "crisis_resilience": {"repair": 0.15, "escalate": 0.10},
    "loyalty_trust":     {"assert": 0.12, "withdraw": 0.08},
}


BALANCE_TRAITS = {
    "risk_tolerance", "conflict_dominance", "withdrawal_tendency",
    "career_priority", "jealousy_threshold", "identity_rigidity",
}


def compute_focused_tension(prompt_a: str, prompt_b: str, category: str) -> float:
    focus_traits = SCENARIO_TRAIT_FOCUS.get(category)
    if not focus_traits:
        distance = compute_trait_distance(prompt_a, prompt_b)
        return 0.15 + distance * 1.0

    tension_components = []
    for t in focus_traits:
        a, b = get_trait(prompt_a, t), get_trait(prompt_b, t)
        divergence = abs(a - b)

        if t in BALANCE_TRAITS:
            # Both-extreme penalty: even identical extreme values create friction
            # (e.g. both high conflict_dominance → power struggles)
            pair_avg = (a + b) / 2.0
            extreme_risk = abs(pair_avg - 0.5) * 2.0  # 0-1, worst at extremes
            tension_components.append(max(divergence, extreme_risk))
        else:
            tension_components.append(divergence)

    focused_distance = sum(tension_components) / len(tension_components)
    return min(1.0, 0.15 + focused_distance * 1.2)


# ---------- Response selection ----------

def select_response_category(
    profile: Dict[str, float],
    tension: float,
    turn: int,
    other_last: str,
    clash_intensity: float,
    scenario_category: str = "",
) -> str:
    scores: Dict[str, float] = {}

    scores["compromise"] = (
        0.3
        + profile["repair"] * 0.25
        + (1.0 - tension) * 0.25
        + (1.0 - profile["assertiveness"]) * 0.1
        + (1.0 - profile["avoidance"]) * 0.1
    )

    scores["assert"] = (
        profile["assertiveness"] * 0.35
        + tension * 0.15
        + (1.0 - profile["avoidance"]) * 0.15
        + (1.0 - profile["deference"]) * 0.15
        + 0.1
    )

    defer_boost = 0.1 if other_last in ("assert", "escalate") else 0.0
    scores["defer"] = (
        profile["deference"] * 0.35
        + (1.0 - profile["assertiveness"]) * 0.15
        + tension * 0.1
        + defer_boost
        + 0.1
    )

    if turn >= 1 and tension > 0.3:
        repair_boost = 0.1 if other_last in ("escalate", "withdraw") else 0.0
        scores["repair"] = (
            profile["repair"] * 0.35
            + (1.0 - profile["avoidance"]) * 0.15
            + min(tension, 0.7) * 0.15
            + repair_boost
            + 0.1
        )
    else:
        scores["repair"] = 0.0

    escalate_boost = 0.1 if other_last in ("defer", "withdraw") else 0.0
    scores["withdraw"] = (
        profile["avoidance"] * 0.2
        + tension * 0.2
        + (1.0 - profile["repair"]) * 0.1
        + 0.04 * min(turn, 3)
    )
    scores["escalate"] = (
        profile["assertiveness"] * 0.15
        + tension * 0.2
        + (1.0 - profile["repair"]) * 0.15
        + (1.0 - profile["avoidance"]) * 0.05
        + escalate_boost
        + 0.04 * min(turn, 3)
    )

    # Trait clash amplifies conflict responses, dampens cooperation
    scores["assert"] += clash_intensity * 0.15
    scores["escalate"] += clash_intensity * 0.2
    scores["compromise"] -= clash_intensity * 0.15
    if profile["avoidance"] > 0.5:
        scores["withdraw"] += clash_intensity * 0.1

    # Apply scenario-category biases
    category_bias = SCENARIO_CATEGORY_BIAS.get(scenario_category, {})
    for cat, boost in category_bias.items():
        if cat in scores:
            scores[cat] += boost

    return max(scores, key=scores.get)


# ---------- Tension dynamics ----------

def compute_tension_delta(
    category: str,
    other_profile: Dict[str, float],
    clash_intensity: float,
) -> float:
    base_deltas = {
        "compromise": -0.08,
        "assert": 0.06,
        "defer": 0.03,
        "repair": -0.12,
        "withdraw": 0.10,
        "escalate": 0.15,
    }
    delta = base_deltas.get(category, 0.0)

    if category == "repair":
        effectiveness = other_profile["repair"] * (1.0 - clash_intensity)
        delta -= effectiveness * 0.08
    elif category == "escalate":
        delta += other_profile["avoidance"] * 0.05
    elif category == "defer":
        delta += other_profile["assertiveness"] * 0.04

    return delta


# ---------- Message generation ----------

def generate_mock_message(
    speaker: str,
    own_prompt: str,
    other_prompt: str,
    history: list,
    tension: float,
    own_last: str,
    other_last: str,
    scenario_category: str = "",
) -> tuple:
    own_profile = compute_behavioral_profile(own_prompt)
    other_profile = compute_behavioral_profile(other_prompt)
    clash_intensity = compute_trait_distance(own_prompt, other_prompt)

    turn = sum(1 for h in history if h["speaker"] == speaker)

    category = select_response_category(
        own_profile, tension, turn, other_last, clash_intensity, scenario_category
    )

    # Resentment override: compromise/defer under high clash builds friction
    original_category = category
    resentment_val = 0.0
    if category in ("compromise", "defer") and clash_intensity > 0.15:
        amplified_clash = clash_intensity ** 0.6
        resentment_val = amplified_clash * (0.2 + tension * 0.25 + turn * 0.12)
        if resentment_val > 0.42:
            category = "escalate"
        elif resentment_val > 0.23:
            category = "strained"

    variants = MESSAGES.get(category, MESSAGES["compromise"])
    thought, spoken = variants[turn % len(variants)]

    dominant_clash = find_dominant_clash(own_prompt, other_prompt)
    modifier = CLASH_MODIFIERS.get(dominant_clash, {}).get(category, "")
    if modifier:
        spoken += modifier

    effective_category = category if category != "strained" else "compromise"
    tension_delta = compute_tension_delta(
        effective_category, other_profile, clash_intensity
    )
    if category == "strained":
        tension_delta += 0.04

    new_tension = max(0.0, min(1.0, tension + tension_delta))

    resentment_info = ""
    if original_category != category:
        resentment_info = f" (override: {original_category}→{category}, resentment={resentment_val:.3f})"

    logger.info(
        "  Turn %d | %s → %-10s | tension %.3f→%.3f (Δ%+.3f) | clash=%.3f%s",
        turn, speaker, category.upper(), tension, new_tension,
        tension_delta, clash_intensity, resentment_info,
    )

    message = f"<InternalThought>{thought}</InternalThought>\n{spoken}"
    return message, new_tension, category


# ---------- LangGraph nodes ----------


# ---------- Environmental Mechanics ----------

EXTERNAL_AGENTS = {
    "family_dynamics": ["Mother-in-Law", "Patriarch", "Nosy Aunt", "Extended Family"],
    "financial": ["Bank Manager", "Siphoning Sibling", "Creditor"],
    "autonomy_identity": ["Society Elders", "Traditional Neighbor"],
    "parenting": ["School Principal", "Overbearing Grandparent"],
    "crisis_resilience": ["Crisis Trigger", "Landlord", "Medical Staff"],
    "loyalty_trust": ["Suspicious Relative", "Legal Counsel", "Anonymous Interferer"],
}

ENVIRONMENT_TEMPLATES = {
    "escalate_reaction": [
        "This is unacceptable! The family reputation is ruined.",
        "You both are acting incredibly selfishly! I will not stand for this.",
        "This is a disaster. What are people going to say?",
    ],
    "repair_reaction": [
        "I'm glad you both are seeing reason.",
        "That's a very mature way to handle it. Thank you.",
        "Okay, we can work with that compromise. Finally some sense.",
    ],
    "neutral_reaction": [
        "We are waiting for your final decision.",
        "The situation remains tense. What will you do?",
        "Time is running out, you need to act.",
    ],
    "limit_break": [
        "THAT'S IT! The relationship is broken beyond repair.",
        "This cannot be fixed. Everything is ruined. You've gone too far.",
        "The damage is done. There is no coming back from this."
    ]
}

def environmental_reaction_node(state: SimulationState):
    scenario = state["scenario_details"]
    category = state["scenario_category"]
    weight = scenario.get("weight", 1)
    dealbreaker = scenario.get("dealbreaker", False)

    # Convert 1-3 weight logic to 1-5 severity scale
    # Dealbreakers push the multiplier higher
    severity = weight * (1.6 if dealbreaker else 1.0) 

    last_a = state["last_category_a"]
    last_b = state["last_category_b"]

    agents = EXTERNAL_AGENTS.get(category, ["External Force"])
    turn = state["turn_count"]
    agent_name = agents[turn % len(agents)]

    # Non-linear mathematics for algorithmic scaling
    stress_delta = 0.0
    happiness_delta = 0.0

    if last_a in ["escalate", "withdraw"] or last_b in ["escalate", "withdraw"]:
        reaction_type = "escalate_reaction"
        # Tension escalates non-linearly based on severity
        stress_delta = (severity ** 1.8) * 3.5  
        
        # High level factor affects happiness exponentially
        if severity >= 4.0:
            happiness_delta -= 20.0 * severity  # Can easily drain 80+ points
        else:
            happiness_delta -= 5.0 * severity
            
    elif last_a in ["repair", "compromise"] and last_b in ["repair", "compromise"]:
        reaction_type = "repair_reaction"
        stress_delta = -(severity ** 1.5) * 4.0
        
        # Highly rewarded if repairing a high-level factor
        if severity >= 4.0:
            happiness_delta += 20.0 * severity  # Outsized reward (e.g. 50+ points)
        else:
            happiness_delta += 10.0 * severity
    else:
        reaction_type = "neutral_reaction"
        stress_delta = severity * 2.0
        happiness_delta -= 2.0 * severity

    # Apply Deltas
    state["accumulated_stress"] += stress_delta
    state["happiness_factor"] += happiness_delta
    
    # Bound tracking
    state["happiness_factor"] = max(0.0, min(100.0, state["happiness_factor"]))
    state["accumulated_stress"] = max(0.0, state["accumulated_stress"])

    # Breakpoint Check (The "Relationship Limit")
    if state["accumulated_stress"] >= state["relationship_limit"] or state["happiness_factor"] == 0:
        reaction_type = "limit_break"
        state["happiness_factor"] = 0.0 # Instant crash
        state["tension_level"] = 1.0

    templates = ENVIRONMENT_TEMPLATES.get(reaction_type)
    message_text = templates[turn % len(templates)]
    
    msg_obj = {
        "speaker": f"Environment [{agent_name}]",
        "message": f"== EXTERNAL REACTION (Severity {severity:.1f}) ==\n{message_text}",
        "_category": "environment",
        "happiness_delta": happiness_delta,
        "stress_delta": stress_delta
    }
    
    state["dialogue_history"].append(msg_obj)
    
    logger.info(
        "  [ENVIRONMENT] %s | Stress Δ: %+.2f (Total: %.2f) | Happiness Δ: %+.2f (Factor: %.2f)",
        agent_name, stress_delta, state["accumulated_stress"], happiness_delta, state["happiness_factor"]
    )

    return state

def scene_master(state: SimulationState):
    scenario = state["scenario_details"]
    category = scenario.get("category", "")
    intro = f"SCENARIO START: {scenario.get('title', 'Unknown')}\n"
    intro += f"Details: {scenario.get('description', '')}\n"

    state["dialogue_history"].append({"speaker": "Scene Master", "message": intro})

    state["scenario_category"] = category
    state["tension_level"] = compute_focused_tension(
        state["agent_a_prompt"], state["agent_b_prompt"], category
    )

    overall_distance = compute_trait_distance(state["agent_a_prompt"], state["agent_b_prompt"])
    profile_a = compute_behavioral_profile(state["agent_a_prompt"])
    profile_b = compute_behavioral_profile(state["agent_b_prompt"])
    clash = find_dominant_clash(state["agent_a_prompt"], state["agent_b_prompt"])

    logger.info("=" * 70)
    logger.info(
        "SCENARIO: %s [%s] | category=%s%s",
        scenario.get("title", "Unknown"), scenario.get("id", "?"),
        category or "unset",
        " [DEALBREAKER]" if scenario.get("dealbreaker") else "",
    )
    logger.info("  Tests: %s", scenario.get("test_reason", "N/A"))
    logger.info("  Scoring: %s", scenario.get("scoring_logic", "N/A"))
    logger.info(
        "  Overall trait distance: %.3f | Focused initial tension: %.3f | Dominant clash: %s",
        overall_distance, state["tension_level"], clash,
    )
    logger.info(
        "  Agent A profile → assert=%.2f avoid=%.2f repair=%.2f defer=%.2f",
        profile_a["assertiveness"], profile_a["avoidance"],
        profile_a["repair"], profile_a["deference"],
    )
    logger.info(
        "  Agent B profile → assert=%.2f avoid=%.2f repair=%.2f defer=%.2f",
        profile_b["assertiveness"], profile_b["avoidance"],
        profile_b["repair"], profile_b["deference"],
    )
    logger.info("-" * 70)

    state["last_category_a"] = ""
    state["last_category_b"] = ""
    state["current_speaker"] = "Agent A"
    return state


def agent_a_node(state: SimulationState):
    msg, new_tension, category = generate_mock_message(
        "Agent A",
        state["agent_a_prompt"],
        state["agent_b_prompt"],
        state["dialogue_history"],
        state["tension_level"],
        state["last_category_a"],
        state["last_category_b"],
        state.get("scenario_category", ""),
    )
    state["dialogue_history"].append(
        {"speaker": "Agent A", "message": msg, "_category": category}
    )
    state["tension_level"] = new_tension
    state["last_category_a"] = category
    state["current_speaker"] = "Agent B"
    return state


def agent_b_node(state: SimulationState):
    msg, new_tension, category = generate_mock_message(
        "Agent B",
        state["agent_b_prompt"],
        state["agent_a_prompt"],
        state["dialogue_history"],
        state["tension_level"],
        state["last_category_b"],
        state["last_category_a"],
        state.get("scenario_category", ""),
    )
    state["dialogue_history"].append(
        {"speaker": "Agent B", "message": msg, "_category": category}
    )
    state["tension_level"] = new_tension
    state["last_category_b"] = category
    state["current_speaker"] = "Agent A"
    state["turn_count"] += 1
    return state


def agent_b_controller(state: SimulationState) -> str:
    # After Agent B, the environment reacts
    return "environment"

def environment_controller(state: SimulationState) -> str:
    # If relationship limits are broken or max turns hit, end the simulation
    if state["accumulated_stress"] >= state["relationship_limit"] or state["happiness_factor"] == 0.0:
        return END
    if state["turn_count"] >= state["max_turns"]:
        return END
    return "agent_a"

# ---------- Build graph ----------

builder = StateGraph(SimulationState)
builder.add_node("scene_master", scene_master)
builder.add_node("agent_a", agent_a_node)
builder.add_node("agent_b", agent_b_node)
builder.add_node("environment", environmental_reaction_node)

builder.add_edge(START, "scene_master")
builder.add_edge("scene_master", "agent_a")
builder.add_edge("agent_a", "agent_b")

# Conditional rules via edge controllers
builder.add_conditional_edges(
    "agent_b", agent_b_controller, {"environment": "environment"}
)

builder.add_conditional_edges(
    "environment", environment_controller, {"agent_a": "agent_a", END: END}
)

simulation_graph = builder.compile()


def run_simulation(
    agent_a_prompt: str,
    agent_b_prompt: str,
    scenario: dict,
    max_turns: int = 5,
):
    initial_state = {
        "agent_a_prompt": agent_a_prompt,
        "agent_b_prompt": agent_b_prompt,
        "scenario_details": scenario,
        "dialogue_history": [],
        "turn_count": 0,
        "max_turns": max_turns,
        "current_speaker": "Scene Master",
        "tension_level": 0.3,
        "last_category_a": "",
        "last_category_b": "",
        "scenario_category": scenario.get("category", ""),
        "accumulated_stress": 0.0,
        "relationship_limit": 150.0,  # 150 stress is the breaking point
        "happiness_factor": 50.0,     # Starts at neutral 50
    }
    result = simulation_graph.invoke(initial_state)

    categories = [
        h.get("_category", "?")
        for h in result["dialogue_history"]
        if h["speaker"] != "Scene Master"
    ]
    logger.info(
        "  SIMULATION COMPLETE | %d turns | final tension: %.3f | response pattern: %s",
        result["turn_count"],
        result["tension_level"],
        " → ".join(categories) if categories else "N/A",
    )

    return result
