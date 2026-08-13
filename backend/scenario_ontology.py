"""Canonical labels shared by persona synthesis and the scenario library.

The planner never accepts labels invented by an LLM.  Scenario generation may
produce prose, but every behavioral dimension must resolve to one of the values
in this module before entering the catalog.
"""

from enum import Enum


class ScenarioDomain(str, Enum):
    HOUSEHOLD_LIFESTYLE = "household_lifestyle"
    EMOTIONAL_CONNECTION = "emotional_connection"
    COMMUNICATION_CONFLICT = "communication_conflict"
    FAMILY_IN_LAWS = "family_in_laws"
    MONEY_ASSETS_DEBT = "money_assets_debt"
    CAREER_RELOCATION = "career_relocation"
    PARENTING_FERTILITY = "parenting_fertility"
    TRUST_JEALOUSY = "trust_jealousy"
    SEX_AFFECTION_INTIMACY = "sex_affection_intimacy"
    HEALTH_CAREGIVING_GRIEF = "health_caregiving_grief"
    IDENTITY_RELIGION_CULTURE = "identity_religion_culture"
    MAJOR_CRISIS = "major_crisis"


DOMAIN_ALLOCATIONS = {
    ScenarioDomain.HOUSEHOLD_LIFESTYLE: 90,
    ScenarioDomain.EMOTIONAL_CONNECTION: 80,
    ScenarioDomain.COMMUNICATION_CONFLICT: 110,
    ScenarioDomain.FAMILY_IN_LAWS: 140,
    ScenarioDomain.MONEY_ASSETS_DEBT: 100,
    ScenarioDomain.CAREER_RELOCATION: 90,
    ScenarioDomain.PARENTING_FERTILITY: 120,
    ScenarioDomain.TRUST_JEALOUSY: 80,
    ScenarioDomain.SEX_AFFECTION_INTIMACY: 65,
    ScenarioDomain.HEALTH_CAREGIVING_GRIEF: 60,
    ScenarioDomain.IDENTITY_RELIGION_CULTURE: 40,
    ScenarioDomain.MAJOR_CRISIS: 25,
}


TRAITS = frozenset({
    "family_deference", "couple_first_orientation", "boundary_strength",
    "partner_advocacy", "social_image_sensitivity", "public_harmony_preference",
    "egalitarianism", "tradition_compliance", "moral_reasoning_style",
    "identity_rigidity", "autonomy_need", "conflict_dominance",
    "withdrawal_tendency", "repair_skill", "co_regulation_capacity",
    "distress_tolerance", "forgiveness_rate", "resentment_accumulation_rate",
    "burnout_vulnerability", "shame_sensitivity", "guilt_susceptibility",
    "financial_mutuality", "risk_tolerance", "security_need", "career_priority",
    "household_order_preference", "jealousy_threshold", "privacy_need",
    "caregiving_flexibility", "parenting_alignment", "hygiene_standard",
    "body_comfort", "sexual_openness", "libido_alignment",
    "intimacy_communication", "ritual_rigidity", "sleep_schedule_compatibility",
    "personal_space_need",
})

VALUES = frozenset({
    "family_duty", "couple_priority", "financial_security", "autonomy",
    "equality", "tradition", "career_fulfillment", "parenthood",
    "privacy", "loyalty", "honesty", "stability", "care", "faith",
    "social_belonging", "growth", "pleasure", "health", "legacy",
})

NEEDS = frozenset({
    "support", "respect", "security", "autonomy", "trust", "connection",
    "fairness", "appreciation", "affection", "privacy", "belonging",
    "reassurance", "rest", "meaning", "sexual_safety", "competence",
})

PROVISIONS = frozenset({
    "advocacy_capacity", "boundary_enforcement", "emotional_support",
    "financial_transparency", "conflict_repair", "co_regulation",
    "practical_care", "affection", "celebration", "reassurance",
    "fair_negotiation", "accountability", "adaptability",
})

MEMORY_TAGS = frozenset({
    "household_labor", "daily_routine", "emotional_responsiveness",
    "conflict_pattern", "family_boundary", "family_money", "career_sacrifice",
    "parenting", "fertility", "trust", "jealousy", "intimacy", "caregiving",
    "grief", "identity", "religion", "culture", "safety", "repair",
    "celebration", "unilateral_decision", "unresolved_request",
})

SAFETY_FLAGS = frozenset({
    "coercive_control", "financial_abuse", "sexual_coercion",
    "physical_intimidation", "isolation", "infidelity", "custody_threat",
    "honor_violence", "addiction_risk",
})


DOMAIN_CATEGORY = {
    ScenarioDomain.HOUSEHOLD_LIFESTYLE: "hygiene_domestic",
    ScenarioDomain.EMOTIONAL_CONNECTION: "crisis_resilience",
    ScenarioDomain.COMMUNICATION_CONFLICT: "crisis_resilience",
    ScenarioDomain.FAMILY_IN_LAWS: "family_dynamics",
    ScenarioDomain.MONEY_ASSETS_DEBT: "financial",
    ScenarioDomain.CAREER_RELOCATION: "autonomy_identity",
    ScenarioDomain.PARENTING_FERTILITY: "parenting",
    ScenarioDomain.TRUST_JEALOUSY: "loyalty_trust",
    ScenarioDomain.SEX_AFFECTION_INTIMACY: "intimacy_sexual",
    ScenarioDomain.HEALTH_CAREGIVING_GRIEF: "crisis_resilience",
    ScenarioDomain.IDENTITY_RELIGION_CULTURE: "autonomy_identity",
    ScenarioDomain.MAJOR_CRISIS: "crisis_resilience",
}


DOMAIN_DIMENSIONS = {
    ScenarioDomain.HOUSEHOLD_LIFESTYLE: {
        "traits": ["household_order_preference", "egalitarianism", "personal_space_need"],
        "values": ["equality", "autonomy", "care"],
        "needs": ["fairness", "rest", "respect"],
        "provisions": ["fair_negotiation", "practical_care", "adaptability"],
        "memory": ["household_labor", "daily_routine"],
    },
    ScenarioDomain.EMOTIONAL_CONNECTION: {
        "traits": ["co_regulation_capacity", "repair_skill", "privacy_need"],
        "values": ["care", "growth", "couple_priority"],
        "needs": ["connection", "support", "appreciation"],
        "provisions": ["emotional_support", "affection", "celebration"],
        "memory": ["emotional_responsiveness", "celebration"],
    },
    ScenarioDomain.COMMUNICATION_CONFLICT: {
        "traits": ["conflict_dominance", "withdrawal_tendency", "repair_skill"],
        "values": ["honesty", "growth", "stability"],
        "needs": ["respect", "fairness", "reassurance"],
        "provisions": ["conflict_repair", "accountability", "co_regulation"],
        "memory": ["conflict_pattern", "repair"],
    },
    ScenarioDomain.FAMILY_IN_LAWS: {
        "traits": ["family_deference", "partner_advocacy", "boundary_strength"],
        "values": ["family_duty", "couple_priority", "tradition"],
        "needs": ["support", "respect", "belonging"],
        "provisions": ["advocacy_capacity", "boundary_enforcement", "fair_negotiation"],
        "memory": ["family_boundary", "unresolved_request"],
    },
    ScenarioDomain.MONEY_ASSETS_DEBT: {
        "traits": ["financial_mutuality", "risk_tolerance", "security_need"],
        "values": ["financial_security", "honesty", "family_duty"],
        "needs": ["security", "trust", "autonomy"],
        "provisions": ["financial_transparency", "fair_negotiation", "accountability"],
        "memory": ["family_money", "unilateral_decision"],
    },
    ScenarioDomain.CAREER_RELOCATION: {
        "traits": ["career_priority", "autonomy_need", "caregiving_flexibility"],
        "values": ["career_fulfillment", "couple_priority", "stability"],
        "needs": ["competence", "support", "fairness"],
        "provisions": ["fair_negotiation", "emotional_support", "adaptability"],
        "memory": ["career_sacrifice", "unilateral_decision"],
    },
    ScenarioDomain.PARENTING_FERTILITY: {
        "traits": ["parenting_alignment", "caregiving_flexibility", "egalitarianism"],
        "values": ["parenthood", "equality", "legacy"],
        "needs": ["support", "fairness", "competence"],
        "provisions": ["practical_care", "fair_negotiation", "co_regulation"],
        "memory": ["parenting", "fertility"],
    },
    ScenarioDomain.TRUST_JEALOUSY: {
        "traits": ["jealousy_threshold", "privacy_need", "boundary_strength"],
        "values": ["loyalty", "honesty", "privacy"],
        "needs": ["trust", "reassurance", "autonomy"],
        "provisions": ["reassurance", "accountability", "boundary_enforcement"],
        "memory": ["trust", "jealousy"],
    },
    ScenarioDomain.SEX_AFFECTION_INTIMACY: {
        "traits": ["sexual_openness", "libido_alignment", "intimacy_communication"],
        "values": ["pleasure", "care", "autonomy"],
        "needs": ["affection", "sexual_safety", "connection"],
        "provisions": ["affection", "reassurance", "fair_negotiation"],
        "memory": ["intimacy", "emotional_responsiveness"],
    },
    ScenarioDomain.HEALTH_CAREGIVING_GRIEF: {
        "traits": ["caregiving_flexibility", "distress_tolerance", "co_regulation_capacity"],
        "values": ["care", "health", "family_duty"],
        "needs": ["support", "rest", "security"],
        "provisions": ["practical_care", "co_regulation", "emotional_support"],
        "memory": ["caregiving", "grief"],
    },
    ScenarioDomain.IDENTITY_RELIGION_CULTURE: {
        "traits": ["tradition_compliance", "identity_rigidity", "autonomy_need"],
        "values": ["faith", "tradition", "autonomy"],
        "needs": ["respect", "belonging", "meaning"],
        "provisions": ["adaptability", "boundary_enforcement", "fair_negotiation"],
        "memory": ["identity", "religion", "culture"],
    },
    ScenarioDomain.MAJOR_CRISIS: {
        "traits": ["distress_tolerance", "co_regulation_capacity", "repair_skill"],
        "values": ["stability", "loyalty", "care"],
        "needs": ["security", "support", "trust"],
        "provisions": ["co_regulation", "practical_care", "accountability"],
        "memory": ["safety", "caregiving", "trust"],
    },
}

