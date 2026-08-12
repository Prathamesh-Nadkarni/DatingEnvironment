import re
import json
import logging
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from state_models import MarriageState

logger = logging.getLogger("mirofish.simulation")


class SimulationState(TypedDict):
    marriage_state: MarriageState
    agent_a: dict
    agent_b: dict
    sampled_traits_a: dict
    sampled_traits_b: dict
    emotional_state_a: dict
    emotional_state_b: dict
    relationship_capital: float
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


def get_trait(prompt_dict: dict, trait: str) -> float:
    try:
        return prompt_dict["traits"].get(trait, {}).get("mean", 0.5)
    except Exception:
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
    # Phase 8 — Hygiene, Sexual Compatibility & Daily Rituals
    "hygiene_standard", "body_comfort", "sexual_openness", "libido_alignment",
    "intimacy_communication", "ritual_rigidity", "sleep_schedule_compatibility",
    "personal_space_need",
]


def compute_behavioral_profile(traits: dict) -> Dict[str, float]:
    return {
        behavior: sum(traits.get(t, 0.5) * w for t, w in components)
        for behavior, components in BEHAVIORAL_COMPONENTS.items()
    }


def compute_trait_distance(prompt_a: dict, prompt_b: dict) -> float:
    diffs = [abs(get_trait(prompt_a, t) - get_trait(prompt_b, t)) for t in KEY_TRAITS]
    return sum(diffs) / len(diffs)


def find_dominant_clash(own_prompt: dict, other_prompt: dict) -> str:
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
            - get_trait(other_prompt, "autonomy_need")
        ),
        "conflict_style": abs(
            get_trait(own_prompt, "conflict_dominance")
            - get_trait(other_prompt, "conflict_dominance")
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
    # Phase 8
    "hygiene_domestic":  ["hygiene_standard", "body_comfort", "household_order_preference", "social_image_sensitivity"],
    "intimacy_sexual":   ["sexual_openness", "libido_alignment", "intimacy_communication", "co_regulation_capacity"],
    "daily_rituals":     ["ritual_rigidity", "sleep_schedule_compatibility", "personal_space_need", "autonomy_need"],
}

# Per-category score boosts for relevant response types
SCENARIO_CATEGORY_BIAS = {
    "family_dynamics":   {"defer": 0.12, "assert": 0.08},
    "financial":         {"assert": 0.10, "compromise": 0.08},
    "autonomy_identity": {"assert": 0.15, "escalate": 0.05},
    "parenting":         {"assert": 0.10, "repair": 0.08},
    "crisis_resilience": {"repair": 0.15, "escalate": 0.10},
    "loyalty_trust":     {"assert": 0.12, "withdraw": 0.08},
    # Phase 8
    "hygiene_domestic":  {"assert": 0.10, "compromise": 0.12},
    "intimacy_sexual":   {"repair": 0.15, "withdraw": 0.10},
    "daily_rituals":     {"compromise": 0.15, "defer": 0.08},
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


# ---------- Stateful Emotion & Response Selection ----------

import math

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def update_emotional_state(state: dict, category: str, other_category: str) -> dict:
    """Updates emotional state based on recent interaction."""
    new_state = state.copy()
    
    if other_category == "escalate":
        new_state["anger"] = min(1.0, new_state["anger"] + 0.2)
        new_state["trust"] = max(0.0, new_state["trust"] - 0.15)
        new_state["safety"] = max(0.0, new_state["safety"] - 0.2)
    elif other_category == "withdraw":
        new_state["hurt"] = min(1.0, new_state["hurt"] + 0.15)
        new_state["safety"] = max(0.0, new_state["safety"] - 0.1)
    elif other_category == "repair":
        new_state["anger"] = max(0.0, new_state["anger"] - 0.15)
        new_state["trust"] = min(1.0, new_state["trust"] + 0.1)
        new_state["safety"] = min(1.0, new_state["safety"] + 0.15)
    elif other_category == "defer":
        # If I forced them to defer, my perceived power goes up, but their resentment might build (handled on their side)
        pass
        
    # If I deferred, resentment builds
    if category == "defer":
        new_state["resentment"] = min(1.0, new_state["resentment"] + 0.1)
        
    return new_state


def select_response_category(
    profile: Dict[str, float],
    tension: float,
    turn: int,
    other_last: str,
    clash_intensity: float,
    emotional_state: dict,
    scenario_category: str = "",
) -> str:
    scores: Dict[str, float] = {}

    anger = emotional_state.get("anger", 0.0)
    safety = emotional_state.get("safety", 0.5)
    resentment = emotional_state.get("resentment", 0.0)
    trust = emotional_state.get("trust", 0.5)

    # Using Sigmoid with logits (raw combinations of trait and state)
    scores["compromise"] = sigmoid(
        -0.5
        + profile["repair"] * 1.0
        + safety * 1.5
        - anger * 1.0
        - resentment * 0.5
    )

    scores["assert"] = sigmoid(
        -1.0
        + profile["assertiveness"] * 2.0
        + tension * 1.0
        - safety * 0.5
    )

    defer_boost = 1.0 if other_last in ("assert", "escalate") else 0.0
    scores["defer"] = sigmoid(
        -1.0
        + profile["deference"] * 1.5
        - profile["assertiveness"] * 1.0
        + defer_boost
    )

    repair_boost = 1.0 if other_last in ("escalate", "withdraw") else 0.0
    scores["repair"] = sigmoid(
        -1.5
        + profile["repair"] * 2.0
        + trust * 1.5
        + safety * 1.0
        - anger * 1.5
        - resentment * 2.0
        + repair_boost
    ) if turn >= 1 else 0.0

    escalate_boost = 1.0 if other_last in ("defer", "withdraw") else 0.0
    scores["withdraw"] = sigmoid(
        -1.0
        + profile["avoidance"] * 2.0
        - safety * 1.5
        + resentment * 1.0
    )
    
    scores["escalate"] = sigmoid(
        -2.0
        + profile["assertiveness"] * 1.0
        + anger * 2.0
        + resentment * 1.5
        - trust * 1.5
        + escalate_boost
    )

    # Apply scenario-category biases
    category_bias = SCENARIO_CATEGORY_BIAS.get(scenario_category, {})
    for cat, boost in category_bias.items():
        if cat in scores:
            scores[cat] += (boost * 2.0)  # scale up for sigmoid bounds

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
    own_prompt: dict,
    other_prompt: dict,
    own_emotional_state: dict,
    history: list,
    tension: float,
    own_last: str,
    other_last: str,
    scenario_category: str = "",
    scenario_desc: str = "",
    user_tone_answers: dict = None,
) -> tuple:
    from llm_analysis import generate_agent_dialogue

    own_profile = compute_behavioral_profile(own_prompt["sampled_traits"] if "sampled_traits" in own_prompt else own_prompt)
    other_profile = compute_behavioral_profile(other_prompt["sampled_traits"] if "sampled_traits" in other_prompt else other_prompt)
    clash_intensity = compute_trait_distance(own_prompt, other_prompt)

    turn = sum(1 for h in history if h["speaker"] == speaker)

    category = select_response_category(
        own_profile, tension, turn, other_last, clash_intensity, own_emotional_state, scenario_category
    )

    # Resentment override is now organically handled by the high resentment multiplier in the sigmoid above,
    # but we'll leave a hard override just in case.
    original_category = category
    if category in ("compromise", "defer") and own_emotional_state.get("resentment", 0) > 0.6:
        if own_emotional_state.get("anger", 0) > 0.5:
            category = "escalate"
        else:
            category = "strained"

    # Generate actual dialogue via LLM matching user tone
    spoken = generate_agent_dialogue(
        scenario_desc=scenario_desc,
        action=category,
        history=history,
        user_tone_answers=user_tone_answers,
        agent_name=speaker
    )
    thought = f"Agent executing action: {category.upper()}"

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
    # Phase 8
    "hygiene_domestic": ["Roommate", "Nosy Neighbor", "Visiting In-Law", "Hygiene-Conscious Friend"],
    "intimacy_sexual": ["Intimacy Counselor", "Well-Meaning Friend", "Intrusive Relative"],
    "daily_rituals": ["Nosy Neighbor", "Morning-Person Colleague", "Traditional Grandparent", "Sleep-Deprived Friend"],
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

    # Apply Deltas to MarriageState (generic event impact)
    m_state = state["marriage_state"]
    # Update state logic
    if reaction_type == "escalate_reaction":
        m_state.relationship_capital = max(0.0, m_state.relationship_capital - severity * 2)
        m_state.trust_a = max(0.0, m_state.trust_a - severity * 0.05)
        m_state.trust_b = max(0.0, m_state.trust_b - severity * 0.05)
        
        # Adaptive Cascades (Phase 2)
        if category == "financial":
            m_state.financial_stability = max(0.0, m_state.financial_stability - severity * 0.1)
            # Cascade: financial stress causes burnout
            m_state.burnout_a += severity * 0.05
            m_state.burnout_b += severity * 0.05
        elif category == "intimacy":
            m_state.intimacy_satisfaction_a = max(0.0, m_state.intimacy_satisfaction_a - severity * 0.1)
            m_state.intimacy_satisfaction_b = max(0.0, m_state.intimacy_satisfaction_b - severity * 0.1)
        elif category == "family_dynamics":
            m_state.family_boundary_health = max(0.0, m_state.family_boundary_health - severity * 0.1)
            # Cascade: family issues spike resentment
            m_state.resentment_a += severity * 0.08
            m_state.resentment_b += severity * 0.08
            
    elif reaction_type == "repair_reaction":
        m_state.relationship_capital = min(100.0, m_state.relationship_capital + severity * 2)
        m_state.trust_a = min(1.0, m_state.trust_a + severity * 0.05)
        m_state.trust_b = min(1.0, m_state.trust_b + severity * 0.05)
        m_state.successful_repairs += 1
        
        # Positive Cascades (Phase 2)
        if category == "financial":
            m_state.financial_stability = min(1.0, m_state.financial_stability + severity * 0.05)
        elif category == "intimacy":
            m_state.intimacy_satisfaction_a = min(1.0, m_state.intimacy_satisfaction_a + severity * 0.05)
            m_state.intimacy_satisfaction_b = min(1.0, m_state.intimacy_satisfaction_b + severity * 0.05)
        
    m_state.update_happiness()
    
    # Bound tracking
    state["happiness_factor"] = (m_state.happiness_a + m_state.happiness_b) / 2.0 * 100.0
    state["accumulated_stress"] = max(0.0, state["accumulated_stress"] + stress_delta)

    # Separation Mechanics (Phase 3)
    import random
    base_risk = 0.0
    if m_state.relationship_capital < 20:
        base_risk = (20 - m_state.relationship_capital) / 20.0
        
    if state["accumulated_stress"] >= state["relationship_limit"]:
        base_risk += 0.5
        
    if base_risk > 0:
        mitigation = ((m_state.commitment_a + m_state.commitment_b) / 2.0 * 0.5) + (m_state.exit_barriers * 0.5)
        p_separation = max(0.0, base_risk - mitigation)
        
        if random.random() < p_separation:
            reaction_type = "limit_break"
            m_state.relationship_capital = 0.0 # Force breakdown
            state["happiness_factor"] = 0.0
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
        state["agent_a"], state["agent_b"], category
    )

    overall_distance = compute_trait_distance(state["agent_a"], state["agent_b"])
    profile_a = compute_behavioral_profile(state["sampled_traits_a"])
    profile_b = compute_behavioral_profile(state["sampled_traits_b"])
    clash = find_dominant_clash(state["agent_a"], state["agent_b"])

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
    # Update state from B's last action if there was one
    if state["last_category_b"]:
        state["emotional_state_a"] = update_emotional_state(
            state["emotional_state_a"], state["last_category_a"], state["last_category_b"]
        )

    msg, new_tension, category = generate_mock_message(
        "Agent A",
        state["agent_a"],
        state["agent_b"],
        state["emotional_state_a"],
        state["dialogue_history"],
        state["tension_level"],
        state["last_category_a"],
        state["last_category_b"],
        state.get("scenario_category", ""),
        scenario_desc=state.get("scenario_details", {}).get("description", ""),
        user_tone_answers=state.get("agent_a", {}).get("answers", {})
    )
    state["dialogue_history"].append(
        {"speaker": "Agent A", "message": msg, "action": category}
    )
    state["tension_level"] = new_tension
    state["last_category_a"] = category
    state["current_speaker"] = "Agent B"
    return state


def agent_b_node(state: SimulationState):
    if state["last_category_a"]:
        state["emotional_state_b"] = update_emotional_state(
            state["emotional_state_b"], state["last_category_b"], state["last_category_a"]
        )
        
    msg, new_tension, category = generate_mock_message(
        "Agent B",
        state["agent_b"],
        state["agent_a"],
        state["emotional_state_b"],
        state["dialogue_history"],
        state["tension_level"],
        state["last_category_b"],
        state["last_category_a"],
        state.get("scenario_category", ""),
        scenario_desc=state.get("scenario_details", {}).get("description", ""),
        user_tone_answers=state.get("agent_b", {}).get("answers", {})
    )
    state["dialogue_history"].append(
        {"speaker": "Agent B", "message": msg, "action": category}
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
    agent_a: dict,
    agent_b: dict,
    sampled_traits_a: dict,
    sampled_traits_b: dict,
    scenario: dict,
    marriage_state: MarriageState,
    max_turns: int = 5,
):
    # Initialize transient emotional states from the persistent MarriageState
    emotional_state_a = {
        "anger": marriage_state.resentment_a,
        "hurt": marriage_state.unresolved_hurt_a,
        "trust": marriage_state.trust_a,
        "safety": marriage_state.emotional_safety_a,
        "resentment": marriage_state.resentment_a
    }
    
    emotional_state_b = {
        "anger": marriage_state.resentment_b,
        "hurt": marriage_state.unresolved_hurt_b,
        "trust": marriage_state.trust_b,
        "safety": marriage_state.emotional_safety_b,
        "resentment": marriage_state.resentment_b
    }

    initial_state = {
        "marriage_state": marriage_state,
        "agent_a": agent_a,
        "agent_b": agent_b,
        "sampled_traits_a": sampled_traits_a,
        "sampled_traits_b": sampled_traits_b,
        "emotional_state_a": emotional_state_a,
        "emotional_state_b": emotional_state_b,
        "relationship_capital": marriage_state.relationship_capital,
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
        "relationship_limit": 150.0,
        "happiness_factor": 50.0,
    }
    result = simulation_graph.invoke(initial_state)

    categories = [
        h.get("_category") or h.get("action", "?")
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
