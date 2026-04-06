from typing import Dict, Any, List, Optional
import json

CORE_DIMENSIONS = [
    "family_deference", "couple_first_orientation", "boundary_strength", "egalitarianism",
    "tradition_compliance", "public_harmony_preference", "partner_advocacy", "financial_mutuality",
    "risk_tolerance", "security_need", "co_regulation_capacity", "distress_tolerance",
    "conflict_dominance", "withdrawal_tendency", "repair_skill", "shame_sensitivity",
    "guilt_susceptibility", "autonomy_need", "caregiving_flexibility", "parenting_alignment",
    "jealousy_threshold", "privacy_need", "career_priority", "resentment_accumulation_rate",
    "forgiveness_rate", "moral_reasoning_style", "burnout_vulnerability", "identity_rigidity",
    "household_order_preference", "social_image_sensitivity"
]

# Diagnostic Mapping Table
# Format: { question_id: { answer_id/val: { dimension: weight } } }
MAPPING_TABLE = {
    # FAMILY & BOUNDARIES
    "3.2": {
        "spouse_primary": {"couple_first_orientation": 0.3, "family_deference": -0.2},
        "parents_primary": {"couple_first_orientation": -0.4, "family_deference": 0.4},
    },
    "4.4": {
        "elders": {"family_deference": 0.4, "public_harmony_preference": 0.3},
        "couple": {"couple_first_orientation": 0.4, "boundary_strength": 0.3},
    },
    "4.5": {
        "defend": {"partner_advocacy": 0.5, "boundary_strength": 0.4},
        "calm": {"co_regulation_capacity": 0.3, "public_harmony_preference": 0.2},
        "silent": {"public_harmony_preference": 0.4, "shame_sensitivity": 0.3, "partner_advocacy": -0.4},
        "private": {"boundary_strength": 0.2, "conflict_dominance": -0.2},
    },
    "15.4": {
        "Protect fairness": {"moral_reasoning_style": 0.4},
        "Protect spouse": {"partner_advocacy": 0.5, "couple_first_orientation": 0.3},
        "Protect parent": {"family_deference": 0.5},
        "De-escalate first": {"public_harmony_preference": 0.4},
        "Stay neutral": {"withdrawal_tendency": 0.2},
    },

    # GENDER & EQUALITY
    "5.3": {
        "adjusts": {"tradition_compliance": 0.4, "egalitarianism": -0.4},
        "redesign": {"egalitarianism": 0.5, "autonomy_need": 0.3},
    },
    "5.4": "scale_egalitarianism_inverse",
    "12.3": {
        "Mother's": {"tradition_compliance": 0.3, "egalitarianism": -0.3},
        "Father's": {"egalitarianism": 0.4},
        "Shared": {"egalitarianism": 0.5},
        "Flexibility-based": {"egalitarianism": 0.3, "autonomy_need": 0.2},
        "Outsource support": {"career_priority": 0.4},
    },

    # FINANCE
    "6.1": {
        "saved": {"security_need": 0.4, "risk_tolerance": -0.3},
        "enjoy": {"risk_tolerance": 0.4, "security_need": -0.2},
    },
    "6.6": {
        "spends": {"security_need": 0.3},
        "controls": {"autonomy_need": 0.5, "financial_mutuality": -0.4},
    },

    # CONFLICT & EMOTIONS (fixed: keys now match actual option strings)
    "7.1": {
        "Talk immediately": {"conflict_dominance": 0.3},
        "Wait/Cool down": {"distress_tolerance": 0.3},
        "Withdraw": {"withdrawal_tendency": 0.5},
        "Use humor": {"repair_skill": 0.3},
        "Seek reassurance": {"co_regulation_capacity": -0.3, "security_need": 0.4},
        "Pretend it's fine": {"public_harmony_preference": 0.3, "withdrawal_tendency": 0.2},
    },
    "7.2": {
        "criticism": {"shame_sensitivity": 0.4},
        "silence": {"withdrawal_tendency": 0.2, "co_regulation_capacity": 0.3},
    },
    "19.2": {
        "fights": {"distress_tolerance": -0.4},
        "resentment": {"resentment_accumulation_rate": 0.5, "burnout_vulnerability": 0.3},
    },

    # ELDERCARE & CAREGIVING
    "14.2": {
        "Responsible": {"caregiving_flexibility": 0.3},
        "Acceptable": {"caregiving_flexibility": 0.2},
        "Last resort": {"caregiving_flexibility": -0.3, "family_deference": 0.3},
        "Wrong": {"caregiving_flexibility": -0.4, "tradition_compliance": 0.3},
        "Depends": {},
    },
    "14.4": {
        "sacrifice": {"caregiving_flexibility": -0.3, "family_deference": 0.4},
        "protect": {"caregiving_flexibility": 0.3, "couple_first_orientation": 0.3},
    },

    # PARENTING
    "13.3": {
        "Never acceptable": {"parenting_alignment": 0.4},
        "Rarely acceptable": {"parenting_alignment": 0.2},
        "Sometimes necessary": {"parenting_alignment": -0.2, "tradition_compliance": 0.2},
        "Depends on context": {},
        "Traditional discipline": {"parenting_alignment": -0.4, "tradition_compliance": 0.3},
    },
    "13.4": {
        "obedience": {"parenting_alignment": -0.3, "tradition_compliance": 0.3},
        "safety": {"parenting_alignment": 0.4, "egalitarianism": 0.2},
    },
    "13.5": {
        "ignore": {"family_deference": 0.3, "parenting_alignment": -0.3},
        "correct": {"parenting_alignment": 0.2, "boundary_strength": 0.2},
        "firm": {"parenting_alignment": 0.4, "boundary_strength": 0.4},
        "adjust": {"family_deference": 0.3, "parenting_alignment": -0.2},
    },

    # JEALOUSY & TRUST
    "17.1": {
        "emotional": {"jealousy_threshold": -0.3},
        "physical": {"jealousy_threshold": 0.2},
    },

    # HOUSEHOLD
    "10.2": {
        "Family rules dominate": {"household_order_preference": 0.3, "family_deference": 0.3},
        "Separate arrangements": {"household_order_preference": 0.2, "autonomy_need": 0.2},
        "Spouse adjust for peace": {"household_order_preference": -0.2, "public_harmony_preference": 0.3},
        "Mutual compromise": {"egalitarianism": 0.2},
        "Depends on ownership": {},
    },
    "5.5": {
        "Whoever notices first": {"egalitarianism": 0.3, "household_order_preference": 0.2},
        "Whoever is less tired": {"egalitarianism": 0.2},
        "Split equally": {"egalitarianism": 0.4, "household_order_preference": 0.3},
        "The woman more often": {"egalitarianism": -0.4, "tradition_compliance": 0.3},
        "The man more often": {"egalitarianism": 0.3},
        "Outsource": {"career_priority": 0.2},
    },

    # FINANCIAL (thin coverage)
    "6.3": {
        "Fully joint": {"financial_mutuality": 0.5},
        "Mostly joint": {"financial_mutuality": 0.3},
        "Mostly separate": {"financial_mutuality": -0.2, "autonomy_need": 0.2},
        "Fully separate": {"financial_mutuality": -0.4, "autonomy_need": 0.3},
        "Depends on stage": {},
    },
    "6.5": {
        "support": {"family_deference": 0.3, "financial_mutuality": -0.2},
        "cap": {"financial_mutuality": 0.3, "boundary_strength": 0.2},
        "refuse": {"boundary_strength": 0.3, "financial_mutuality": 0.2},
        "delay": {"withdrawal_tendency": 0.2},
        "evaluate": {"financial_mutuality": 0.3},
    },

    # SOCIAL IMAGE (used in engine now)
    "11.3": {
        "embarrassing_family": {"social_image_sensitivity": 0.4, "public_harmony_preference": 0.3},
        "not_protecting_spouse": {"partner_advocacy": 0.4},
    },

    # MORAL LOGIC
    "20.1": {
        "fair": {"moral_reasoning_style": 0.5},
        "preserves": {"public_harmony_preference": 0.4, "identity_rigidity": -0.2},
    },
    "20.3": {
        "duty": {"tradition_compliance": 0.4, "guilt_susceptibility": 0.3},
        "wellbeing": {"autonomy_need": 0.4},
    },
}

# Scale questions: map score (1-7) to trait shifts via direction (+1 = agree→high, -1 = agree→low)
SCALE_MAPPINGS = {
    "1.4": {"family_deference": -1, "boundary_strength": 1},
    "1.5": {"egalitarianism": -1},
    "4.1": {"family_deference": 1},
    "4.2": {"boundary_strength": 1, "autonomy_need": 1},
    "4.3": {"boundary_strength": 1, "couple_first_orientation": 1},
    "4.6": {"family_deference": 1, "boundary_strength": -1},
    "5.1": {"egalitarianism": 1},
    "7.3": {"public_harmony_preference": 1, "withdrawal_tendency": 1},
    "7.4": {"co_regulation_capacity": 1, "distress_tolerance": 1},
    "7.6": {"conflict_dominance": 1, "repair_skill": -1},
    "8.2": {"co_regulation_capacity": -1, "burnout_vulnerability": 1},
    "9.5": {"social_image_sensitivity": 1, "public_harmony_preference": 1},
    "11.1": {"social_image_sensitivity": 1},
    "11.4": {"public_harmony_preference": 1, "family_deference": 1},
    "12.1": {"career_priority": 1},
    "12.4": {"distress_tolerance": 1},
    "14.1": {"family_deference": 1, "caregiving_flexibility": -1},
    "15.1": {"partner_advocacy": 1, "boundary_strength": 1},
    "15.3": {"partner_advocacy": 1},
    "16.1": {"privacy_need": 1, "boundary_strength": 1},
    "16.4": {"privacy_need": 1, "autonomy_need": 1},
    "19.1": {"distress_tolerance": 1, "resentment_accumulation_rate": 1},
    "19.3": {"co_regulation_capacity": 1},
    "19.6": {"burnout_vulnerability": 1},
    "19.7": {"resentment_accumulation_rate": 1, "forgiveness_rate": -1},
    "19.11": {"egalitarianism": 1},
    "20.4": {"boundary_strength": 1, "autonomy_need": 1},
    "20.7": {"public_harmony_preference": 1, "moral_reasoning_style": -1},
    "22.1": {"autonomy_need": 1, "couple_first_orientation": 1},
    "22.2": {"family_deference": 1},
    "22.3": {"egalitarianism": 1, "moral_reasoning_style": 1},
    "22.4": {"public_harmony_preference": 1, "withdrawal_tendency": 1},
    "22.5": {"tradition_compliance": 1, "identity_rigidity": 1},
    "22.6": {"public_harmony_preference": 1, "conflict_dominance": -1},
    "9.1": {"tradition_compliance": 1, "identity_rigidity": 1},

    # --- Previously dead: parenting_alignment, caregiving_flexibility ---
    "13.2": {"parenting_alignment": -1, "family_deference": 1},
    "10.1": {"household_order_preference": 1},
    "17.2": {"jealousy_threshold": -1},

    # --- Strengthen thin coverage ---
    "6.2": {"financial_mutuality": 1},
    "19.12": {"guilt_susceptibility": 1},
    "20.5": {"forgiveness_rate": 1},
    "18.5": {"repair_skill": 1},
    "18.10": {"repair_skill": 1},
}

class PersonaEngine:
    def __init__(self):
        self.ideal_traits = {dim: 0.5 for dim in CORE_DIMENSIONS}
        self.enacted_traits = {dim: 0.5 for dim in CORE_DIMENSIONS}
        self.ambivalence_map = {}
        self.trigger_map = {"hot": [], "slow": []}
        self.narrative_hits = []

    def synthesize(self, raw_answers: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the 9-step interpretation pipeline."""
        # Step 1: Broad Ideal Seeding (From Screener)
        self._seed_ideals(raw_answers)
        
        # Step 2: Enacted Behavior (From SJTs and Scales)
        self._process_enacted(raw_answers)
        
        # Step 3: Conflict & Ambivalence Detection
        self._detect_contradictions()
        
        # Step 4: Narrative Clustering
        clusters = self._calculate_clusters()
        
        # Step 5: Final Summary
        summary = self._generate_summary(clusters)
        
        return {
            "enacted_traits": self.enacted_traits,
            "ideal_traits": self.ideal_traits,
            "ambivalence": self.ambivalence_map,
            "clusters": clusters,
            "summary": summary,
            "system_prompt": self._generate_prompt(clusters, summary)
        }

    def _seed_ideals(self, answers):
        # S-prefixed questions represent stated ideals
        for q_id, val in answers.items():
            if not q_id.startswith("S."): continue
            
            # Simplified ideal mapping
            if q_id == "S.2":
                if val == "emotional": self.ideal_traits["co_regulation_capacity"] += 0.2
                else: self.ideal_traits["security_need"] += 0.2
            if q_id == "S.5": # Marriage Importance
                try: 
                    weight = (float(val) - 3) / 10.0
                    self.ideal_traits["identity_rigidity"] += weight
                except: pass

    def _process_enacted(self, answers):
        for q_id, val in answers.items():
            if q_id in MAPPING_TABLE:
                mapping = MAPPING_TABLE[q_id]
                if isinstance(mapping, str):
                    self._handle_special_scales(q_id, val, mapping)
                elif val in mapping:
                    for dim, shift in mapping[val].items():
                        self.enacted_traits[dim] = max(0.0, min(1.0, self.enacted_traits[dim] + shift))

            if q_id in SCALE_MAPPINGS:
                self._apply_scale_mapping(q_id, val)

    def _apply_scale_mapping(self, q_id, val):
        try:
            score = float(val)
            for dim, direction in SCALE_MAPPINGS[q_id].items():
                shift = (score - 4) / 10.0 * direction
                self.enacted_traits[dim] = max(0.0, min(1.0, self.enacted_traits[dim] + shift))
        except (ValueError, TypeError):
            pass

    def _handle_special_scales(self, q_id, val, scale_type):
        try:
            score = float(val)
            if scale_type == "scale_egalitarianism_inverse":
                shift = (score - 4) / 10.0
                self.enacted_traits["egalitarianism"] -= shift
                self.enacted_traits["tradition_compliance"] += shift
        except (ValueError, TypeError):
            pass

    def _detect_contradictions(self):
        # Detect: Modern Ideal vs Traditional Enactment
        ideal_egl = self.ideal_traits.get("egalitarianism", 0.5)
        enacted_egl = self.enacted_traits.get("egalitarianism", 0.5)
        
        if ideal_egl > 0.7 and enacted_egl < 0.4:
            self.ambivalence_map["equality"] = "Intellectual Egalitarian / Behavioral Deference (Conflict likely)"
            
        # Detect: Harmony Idol vs Protective Instinct
        harm = self.enacted_traits.get("public_harmony_preference", 0.5)
        adv = self.enacted_traits.get("partner_advocacy", 0.5)
        if harm > 0.7 and adv > 0.6:
            self.ambivalence_map["loyalty"] = "The Protector's Paradox (Wants to defend spouse but fears public rupture)"

    def _calculate_clusters(self):
        clusters = {
            "power": self._cluster_power(),
            "emotion": self._cluster_emotion(),
            "future": self._cluster_future()
        }
        return clusters

    def _cluster_power(self):
        def_v = self.enacted_traits["family_deference"]
        bnd_v = self.enacted_traits["boundary_strength"]
        if def_v > 0.6 and bnd_v < 0.4: return "Deferential (Centered on parental approval)"
        if def_v < 0.4 and bnd_v > 0.6: return "Sovereign (Marriage as an independent unit)"
        return "Collaborative (Negotiates between unit and family)"

    def _cluster_emotion(self):
        reg = self.enacted_traits["co_regulation_capacity"]
        wth = self.enacted_traits["withdrawal_tendency"]
        if reg > 0.6 and wth < 0.4: return "Secure/Engaged"
        if wth > 0.6: return "Avoidant/Withdrawn"
        return "Anxious/Reassurance-Seeking"

    def _cluster_future(self):
        mut = self.enacted_traits["financial_mutuality"]
        risk = self.enacted_traits["risk_tolerance"]
        if mut > 0.7: return "Communal Builder"
        return "Individualist/Separate"

    def _generate_summary(self, clusters):
        return f"This persona is a {clusters['power']} operator who values {clusters['emotion']} emotional dynamics and approaches the future as a {clusters['future']}."

    def _generate_prompt(self, clusters, summary):
        rounded = {k: round(v, 4) for k, v in self.enacted_traits.items()}
        return f"""You are the 'Inner Parliament' for this persona.
CONTEXT: {summary}
CLUSTERS: {json.dumps(clusters)}
TRAITS (ENACTED): {json.dumps(rounded, indent=1)}
AMBIVALENCE: {json.dumps(self.ambivalence_map, indent=1)}

SIMULATION INSTRUCTION:
- Use <InternalThought> to resolve the conflict between what you WANT (Ideals) and what you DO (Enacted traits).
- In Indian family scenarios, prioritize 'Dignity' and 'Harmony' but track 'Resentment' if you are forced to sacrifice Fairness.
"""

def analyze_answers(answers: Dict[str, Any]) -> str:
    engine = PersonaEngine()
    result = engine.synthesize(answers)
    return result["system_prompt"]
