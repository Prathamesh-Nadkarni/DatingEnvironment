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
        "parents_primary": {"couple_first_orientation": -0.4, "family_deference": 0.4}
    },
    "4.4": {
        "elders": {"family_deference": 0.4, "public_harmony_preference": 0.3},
        "couple": {"couple_first_orientation": 0.4, "boundary_strength": 0.3}
    },
    "4.5": {
        "defend": {"partner_advocacy": 0.5, "boundary_strength": 0.4},
        "calm": {"co_regulation_capacity": 0.3, "public_harmony_preference": 0.2},
        "silent": {"public_harmony_preference": 0.4, "shame_sensitivity": 0.3, "partner_advocacy": -0.4},
        "private": {"boundary_strength": 0.2, "conflict_dominance": -0.2}
    },
    "15.4": {
        "fairness": {"moral_reasoning_style": 0.4},
        "spouse": {"partner_advocacy": 0.5, "couple_first_orientation": 0.3},
        "parent": {"family_deference": 0.5},
        "de-escalate": {"public_harmony_preference": 0.4}
    },

    # GENDER & EQUALITY
    "5.3": {
        "adjusts": {"tradition_compliance": 0.4, "egalitarianism": -0.4},
        "redesign": {"egalitarianism": 0.5, "autonomy_need": 0.3}
    },
    "5.4": "scale_egalitarianism_inverse", # 1=low trad, 7=high trad
    "12.3": {
        "mother's": {"tradition_compliance": 0.3, "egalitarianism": -0.3},
        "father's": {"egalitarianism": 0.4},
        "shared": {"egalitarianism": 0.5},
        "outsource": {"career_priority": 0.4}
    },

    # FINANCE
    "6.1": {
        "saved": {"security_need": 0.4, "risk_tolerance": -0.3},
        "enjoy": {"risk_tolerance": 0.4, "security_need": -0.2}
    },
    "6.6": {
        "spends": {"security_need": 0.3},
        "controls": {"autonomy_need": 0.5, "financial_mutuality": -0.4}
    },

    # CONFLICT & EMOTIONS
    "7.1": {
        "talk": {"conflict_dominance": 0.3},
        "wait": {"distress_tolerance": 0.3},
        "withdraw": {"withdrawal_tendency": 0.5},
        "humor": {"repair_skill": 0.2},
        "reassurance": {"co_regulation_capacity": -0.3, "security_need": 0.4}
    },
    "7.2": {
        "criticism": {"shame_sensitivity": 0.4},
        "silence": {"withdrawal_tendency": 0.2, "co_regulation_capacity": 0.3}
    },
    "19.2": {
        "fights": {"distress_tolerance": -0.4},
        "resentment": {"resentment_accumulation_rate": 0.5, "burnout_vulnerability": 0.3}
    },

    # MORAL LOGIC
    "20.1": {
        "fair": {"moral_reasoning_style": 0.5},
        "preserves": {"public_harmony_preference": 0.4, "identity_rigidity": -0.2}
    },
    "20.3": {
        "duty": {"tradition_compliance": 0.4, "guilt_susceptibility": 0.3},
        "wellbeing": {"autonomy_need": 0.4}
    }
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
                
                # Handle Scales via pre-defined logic or explicit dict
                if isinstance(mapping, str):
                    self._handle_special_scales(q_id, val, mapping)
                else:
                    # Categorical Mapping
                    if val in mapping:
                        for dim, shift in mapping[val].items():
                            self.enacted_traits[dim] = max(0.0, min(1.0, self.enacted_traits[dim] + shift))

    def _handle_special_scales(self, q_id, val, type):
        try:
            score = float(val)
            if type == "scale_egalitarianism_inverse":
                # 1=Fair, 7=Traditional
                shift = (score - 4) / 10.0 # 0.3 for 7, -0.3 for 1
                self.enacted_traits["egalitarianism"] -= shift
                self.enacted_traits["tradition_compliance"] += shift
        except: pass

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
        return f"""You are the 'Inner Parliament' for this persona.
CONTEXT: {summary}
CLUSTERS: {json.dumps(clusters)}
TRAITS (ENACTED): {json.dumps(self.enacted_traits, indent=1)}
AMBIVALENCE: {json.dumps(self.ambivalence_map, indent=1)}

SIMULATION INSTRUCTION:
- Use <InternalThought> to resolve the conflict between what you WANT (Ideals) and what you DO (Enacted traits).
- In Indian family scenarios, prioritize 'Dignity' and 'Harmony' but track 'Resentment' if you are forced to sacrifice Fairness.
"""

def analyze_answers(answers: Dict[str, Any]) -> str:
    engine = PersonaEngine()
    result = engine.synthesize(answers)
    return result["system_prompt"]
