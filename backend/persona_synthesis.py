from typing import Dict, Any, List, Optional
import json

from pydantic import BaseModel, Field

# --- V2 Evidence Store Models ---
class TraitEvidence(BaseModel):
    trait: str
    value: float
    weight: float = 1.0
    source_question: str
    context: Dict[str, str] = Field(default_factory=dict) # e.g. {"actor": "parents", "stress": "public_conflict"}
    evidence_type: str # "perception", "emotion", "impulse", "behavior", "reflection"

class EvidenceStore:
    def __init__(self):
        self.evidence_log: List[TraitEvidence] = []
        
    def add_evidence(self, evidence: TraitEvidence):
        self.evidence_log.append(evidence)
        
    def aggregate_traits(self) -> Dict[str, Any]:
        """Deterministically aggregate baseline traits from the evidence."""
        trait_groups = {}
        for ev in self.evidence_log:
            if ev.trait not in trait_groups:
                trait_groups[ev.trait] = []
            trait_groups[ev.trait].append(ev)
            
        results = {}
        for trait, ev_list in trait_groups.items():
            total_weight = sum(ev.weight for ev in ev_list)
            if total_weight == 0:
                continue
                
            mean_val = sum(ev.value * ev.weight for ev in ev_list) / total_weight
            
            # Simple confidence proxy: more evidence = higher confidence, capped at 0.95
            evidence_count = len(ev_list)
            confidence = min(0.95, 0.3 + (evidence_count * 0.1))
            
            # Contradiction proxy: variance in the values
            variance = sum((ev.value - mean_val) ** 2 for ev in ev_list) / evidence_count if evidence_count > 1 else 0.0
            contradiction_score = min(1.0, variance * 2.0)
            
            results[trait] = {
                "mean": round(mean_val, 3),
                "confidence": round(confidence, 3),
                "evidence_count": evidence_count,
                "contradiction_score": round(contradiction_score, 3),
                "context_variance": round(variance, 3)
            }
            
        return results

CORE_DIMENSIONS = [
    "family_deference", "couple_first_orientation", "boundary_strength", "egalitarianism",
    "tradition_compliance", "public_harmony_preference", "partner_advocacy", "financial_mutuality",
    "risk_tolerance", "security_need", "co_regulation_capacity", "distress_tolerance",
    "conflict_dominance", "withdrawal_tendency", "repair_skill", "shame_sensitivity",
    "guilt_susceptibility", "autonomy_need", "caregiving_flexibility", "parenting_alignment",
    "jealousy_threshold", "privacy_need", "career_priority", "resentment_accumulation_rate",
    "forgiveness_rate", "moral_reasoning_style", "burnout_vulnerability", "identity_rigidity",
    "household_order_preference", "social_image_sensitivity",
    # Phase 8 — Hygiene, Sexual Compatibility & Daily Rituals
    "hygiene_standard", "body_comfort", "sexual_openness", "libido_alignment",
    "intimacy_communication", "ritual_rigidity", "sleep_schedule_compatibility",
    "personal_space_need",
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

    # ---- HYGIENE & DOMESTIC STANDARDS (Section 24) ----
    "24.2": {
        "messy": {"hygiene_standard": 0.4, "household_order_preference": 0.3},
        "sterile": {"hygiene_standard": -0.2, "body_comfort": 0.3},
    },
    "24.3": {
        "direct": {"hygiene_standard": 0.4, "conflict_dominance": 0.2, "repair_skill": 0.2},
        "hints": {"hygiene_standard": 0.2, "withdrawal_tendency": 0.2},
        "adjust": {"hygiene_standard": -0.3, "public_harmony_preference": 0.3},
        "letgo": {"hygiene_standard": -0.4, "body_comfort": 0.3},
    },
    "24.4": {
        "Normal and comfortable": {"body_comfort": 0.5},
        "Tolerable": {"body_comfort": 0.2},
        "Should be private": {"body_comfort": -0.3, "hygiene_standard": 0.2},
        "Deeply uncomfortable": {"body_comfort": -0.5, "hygiene_standard": 0.4},
    },
    "24.5": {
        "Daily": {"hygiene_standard": 0.5, "household_order_preference": 0.4},
        "2-3 times a week": {"hygiene_standard": 0.3, "household_order_preference": 0.2},
        "Weekly": {"hygiene_standard": 0.1},
        "When visibly dirty": {"hygiene_standard": -0.3},
        "Outsource entirely": {"career_priority": 0.2},
    },

    # ---- SEXUAL COMPATIBILITY (Section 25) ----
    "25.2": {
        "Very adventurous/experimental": {"sexual_openness": 0.5, "libido_alignment": 0.3},
        "Open to trying new things": {"sexual_openness": 0.3, "libido_alignment": 0.2},
        "Moderate \u2014 some variety": {"sexual_openness": 0.1},
        "Prefer familiar and comfortable": {"sexual_openness": -0.2},
        "Very traditional/vanilla": {"sexual_openness": -0.4, "tradition_compliance": 0.2},
    },
    "25.4": {
        "higher": {"libido_alignment": 0.3, "sexual_openness": 0.2},
        "middle": {"intimacy_communication": 0.3, "repair_skill": 0.2},
        "lower": {"libido_alignment": -0.2, "boundary_strength": 0.2},
        "causes": {"intimacy_communication": 0.5, "co_regulation_capacity": 0.3},
        "spontaneous": {"sexual_openness": 0.2, "ritual_rigidity": -0.2},
    },
    "25.5": {
        "passion": {"sexual_openness": 0.3, "libido_alignment": 0.3},
        "safety": {"intimacy_communication": 0.4, "co_regulation_capacity": 0.2},
    },
    "25.6": {
        "Be mutual and equal": {"egalitarianism": 0.2, "intimacy_communication": 0.3},
        "Usually come from one partner": {"sexual_openness": -0.2},
        "Be spontaneous and unplanned": {"sexual_openness": 0.2, "ritual_rigidity": -0.2},
        "Depend entirely on mood": {"libido_alignment": -0.2},
        "Be discussed openly": {"intimacy_communication": 0.5},
    },

    # ---- DAILY RITUALS & ROUTINES (Section 26) ----
    "26.2": {
        "predictable": {"ritual_rigidity": 0.4, "household_order_preference": 0.3},
        "flexible": {"ritual_rigidity": -0.4, "autonomy_need": 0.2},
    },
    "26.3": {
        "Shared (breakfast together, etc.)": {"ritual_rigidity": 0.3, "personal_space_need": -0.3},
        "Parallel (same space, own routine)": {"ritual_rigidity": 0.1, "personal_space_need": 0.1},
        "Independent (no coordination needed)": {"personal_space_need": 0.4, "ritual_rigidity": -0.2},
        "Family-centered (prayer/puja together)": {"ritual_rigidity": 0.4, "tradition_compliance": 0.3},
    },
    "26.5": {
        "Early to bed, early to rise": {"sleep_schedule_compatibility": 0.4, "ritual_rigidity": 0.2},
        "Night owl": {"sleep_schedule_compatibility": -0.3, "personal_space_need": 0.2},
        "Flexible, no fixed pattern": {"sleep_schedule_compatibility": 0.1, "ritual_rigidity": -0.3},
        "Depends on work demands": {"career_priority": 0.2},
    },
    "26.6": {
        "adapt": {"sleep_schedule_compatibility": 0.3, "public_harmony_preference": 0.2},
        "make_them": {"conflict_dominance": 0.3, "sleep_schedule_compatibility": -0.2},
        "separate": {"personal_space_need": 0.4, "sleep_schedule_compatibility": -0.3},
        "compromise": {"repair_skill": 0.3, "sleep_schedule_compatibility": 0.2},
        "accept": {"personal_space_need": 0.3, "distress_tolerance": 0.2},
    },
    "26.7": {
        "Almost none \u2014 I want togetherness": {"personal_space_need": -0.5},
        "30 minutes to 1 hour": {"personal_space_need": -0.1},
        "1-2 hours": {"personal_space_need": 0.2},
        "2+ hours": {"personal_space_need": 0.4},
        "I recharge heavily alone": {"personal_space_need": 0.5, "withdrawal_tendency": 0.2},
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

    # ---- Phase 8: Hygiene, Sexual Compat, Daily Rituals scales ----
    "24.1": {"hygiene_standard": 1},
    "25.1": {"sexual_openness": 1, "libido_alignment": 1},
    "25.3": {"intimacy_communication": 1},
    "26.1": {"ritual_rigidity": 1},
    "26.4": {"ritual_rigidity": 1, "personal_space_need": -1},
}

class PersonaEngine:
    def __init__(self):
        # We start with a baseline mean of 0.5 for all traits
        self.ideal_traits = {dim: {"mean": 0.5, "evidence": []} for dim in CORE_DIMENSIONS}
        self.enacted_traits = {dim: {"mean": 0.5, "evidence": []} for dim in CORE_DIMENSIONS}
        self.ambivalence_map = {}
        self.text_answers = {}
        
    def _compile_distributions(self, traits_dict):
        compiled = {}
        for dim, data in traits_dict.items():
            ev = data["evidence"]
            ev_count = len(ev)
            if ev_count == 0:
                compiled[dim] = {
                    "mean": data["mean"],
                    "variance": 0.1, # Default high uncertainty if no evidence
                    "confidence": 0.1,
                    "evidence_count": 0,
                    "contradiction_score": 0.0
                }
                continue
                
            # Compute contradiction (sum of magnitudes of opposite signs)
            positives = sum([e for e in ev if e > 0])
            negatives = abs(sum([e for e in ev if e < 0]))
            
            # Contradiction is high if both positive and negative evidence exist
            contradiction_score = min(positives, negatives) / max(positives, negatives, 0.1)
            
            # Variance increases with contradiction and decreases with evidence count
            variance = max(0.01, 0.1 - (ev_count * 0.01) + (contradiction_score * 0.05))
            
            # Confidence is high if lots of evidence and low contradiction
            confidence = min(1.0, (ev_count * 0.15) * (1 - (contradiction_score * 0.5)))
            
            compiled[dim] = {
                "mean": round(data["mean"], 3),
                "variance": round(variance, 3),
                "confidence": round(confidence, 3),
                "evidence_count": ev_count,
                "contradiction_score": round(contradiction_score, 3)
            }
        return compiled

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
        
        return self._generate_prompt(clusters, summary, raw_answers)

    def _seed_ideals(self, answers):
        # S-prefixed questions represent stated ideals
        for q_id, val in answers.items():
            if not q_id.startswith("S."): continue
            
            # Simplified ideal mapping
            if q_id == "S.2":
                if val == "emotional": 
                    self.ideal_traits["co_regulation_capacity"]["mean"] = min(1.0, self.ideal_traits["co_regulation_capacity"]["mean"] + 0.2)
                    self.ideal_traits["co_regulation_capacity"]["evidence"].append(0.2)
                else: 
                    self.ideal_traits["security_need"]["mean"] = min(1.0, self.ideal_traits["security_need"]["mean"] + 0.2)
                    self.ideal_traits["security_need"]["evidence"].append(0.2)
            if q_id == "S.5": # Marriage Importance
                try: 
                    weight = (float(val) - 3) / 10.0
                    self.ideal_traits["identity_rigidity"]["mean"] = max(0.0, min(1.0, self.ideal_traits["identity_rigidity"]["mean"] + weight))
                    self.ideal_traits["identity_rigidity"]["evidence"].append(weight)
                except: pass

    def _process_enacted(self, answers):
        if not hasattr(self, 'evidence_store'):
            self.evidence_store = EvidenceStore()
            
        for q_id, val in answers.items():
            # Handle probe_group dictionaries
            action_val = val.get("action") if isinstance(val, dict) else val
            emotion_val = val.get("emotion") if isinstance(val, dict) else None
            reflection_val = val.get("reflection") if isinstance(val, dict) else None

            if q_id in MAPPING_TABLE:
                mapping = MAPPING_TABLE[q_id]
                if isinstance(mapping, str):
                    self._handle_special_scales(q_id, action_val, mapping)
                elif action_val in mapping:
                    for dim, shift in mapping[action_val].items():
                        self.enacted_traits[dim]["mean"] = max(0.0, min(1.0, self.enacted_traits[dim]["mean"] + shift))
                        self.enacted_traits[dim]["evidence"].append(shift)
                        
                        # Add to EvidenceStore
                        self.evidence_store.add_evidence(TraitEvidence(
                            trait=dim,
                            value=0.5 + shift,
                            weight=abs(shift),
                            source_question=q_id,
                            evidence_type="behavior"
                        ))

            if q_id in SCALE_MAPPINGS:
                self._apply_scale_mapping(q_id, action_val)
                
            # Capture free-text answers (long strings not in predefined options/scales)
            if q_id not in MAPPING_TABLE and q_id not in SCALE_MAPPINGS:
                if isinstance(action_val, str) and len(action_val.strip()) > 3:
                    # Exclude simple demographics
                    if q_id not in ["0.1", "0.2", "0.3", "0.4"]:
                        self.text_answers[q_id] = action_val
                        
            # Capture probe_group context
            if isinstance(val, dict):
                if emotion_val:
                    self.text_answers[f"{q_id}_emotion"] = emotion_val
                if reflection_val:
                    self.text_answers[f"{q_id}_reflection"] = reflection_val

    def _apply_scale_mapping(self, q_id, val):
        try:
            score = float(val)
            for dim, direction in SCALE_MAPPINGS[q_id].items():
                shift = (score - 4) / 10.0 * direction
                self.enacted_traits[dim]["mean"] = max(0.0, min(1.0, self.enacted_traits[dim]["mean"] + shift))
                self.enacted_traits[dim]["evidence"].append(shift)
        except (ValueError, TypeError):
            pass

    def _handle_special_scales(self, q_id, val, scale_type):
        try:
            score = float(val)
            if scale_type == "scale_egalitarianism_inverse":
                shift = (score - 4) / 10.0
                self.enacted_traits["egalitarianism"]["mean"] = max(0.0, min(1.0, self.enacted_traits["egalitarianism"]["mean"] - shift))
                self.enacted_traits["egalitarianism"]["evidence"].append(-shift)
                self.enacted_traits["tradition_compliance"]["mean"] = max(0.0, min(1.0, self.enacted_traits["tradition_compliance"]["mean"] + shift))
                self.enacted_traits["tradition_compliance"]["evidence"].append(shift)
        except (ValueError, TypeError):
            pass

    def _detect_contradictions(self):
        # Detect: Modern Ideal vs Traditional Enactment
        ideal_egl = self.ideal_traits["egalitarianism"]["mean"]
        enacted_egl = self.enacted_traits["egalitarianism"]["mean"]
        
        if ideal_egl > 0.7 and enacted_egl < 0.4:
            self.ambivalence_map["equality"] = "Intellectual Egalitarian / Behavioral Deference (Conflict likely)"
            
        # Detect: Harmony Idol vs Protective Instinct
        harm = self.enacted_traits["public_harmony_preference"]["mean"]
        adv = self.enacted_traits["partner_advocacy"]["mean"]
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
        def_v = self.enacted_traits["family_deference"]["mean"]
        bnd_v = self.enacted_traits["boundary_strength"]["mean"]
        if def_v > 0.6 and bnd_v < 0.4: return "Deferential (Centered on parental approval)"
        if def_v < 0.4 and bnd_v > 0.6: return "Sovereign (Marriage as an independent unit)"
        return "Collaborative (Negotiates between unit and family)"

    def _cluster_emotion(self):
        reg = self.enacted_traits["co_regulation_capacity"]["mean"]
        wth = self.enacted_traits["withdrawal_tendency"]["mean"]
        if reg > 0.6 and wth < 0.4: return "Secure/Engaged"
        if wth > 0.6: return "Avoidant/Withdrawn"
        return "Anxious/Reassurance-Seeking"

    def _cluster_future(self):
        mut = self.enacted_traits["financial_mutuality"]["mean"]
        if mut > 0.7: return "Communal Builder"
        return "Individualist/Separate"

    def _generate_summary(self, clusters):
        return f"This persona is a {clusters['power']} operator who values {clusters['emotion']} emotional dynamics and approaches the future as a {clusters['future']}."

    def _generate_prompt(self, clusters, summary, raw_answers):
        # SPRINT 3: Evidence Aggregation
        # Instead of compiling legacy distributions, we aggregate from our rich EvidenceStore.
        distributions = self.evidence_store.aggregate_traits()
        
        # SPRINT 3: Reactive vs Deliberative Policy calculation
        # We calculate an 'effective_policy' using a simplified stress activation model
        # For this prototype, we'll assume higher burnout/shame increases the reactive_weight
        burnout = self.enacted_traits["burnout_vulnerability"]["mean"]
        shame = self.enacted_traits["shame_sensitivity"]["mean"]
        stress_activation = min(1.0, (burnout + shame) / 2.0)
        
        # effective_policy = (reactive_policy * reactive_weight) + (deliberate_policy * (1 - reactive_weight))
        # Here we just represent this concept as a text modifier for the LLM
        policy_directive = f"STRESS ACTIVATION: {round(stress_activation, 2)}\n"
        if stress_activation > 0.6:
            policy_directive += "REACTIVE POLICY DOMINANT: Under stress, this persona defaults to instinctual, protective behaviors rather than deliberative ideals."
        else:
            policy_directive += "DELIBERATIVE POLICY DOMINANT: Under stress, this persona is able to self-regulate and act according to their ideals."
            
        text_context = "\n".join([f"Q({k}): {v}" for k, v in self.text_answers.items()])
        
        formatted_dists = {}
        for dim, data in distributions.items():
            formatted_dists[dim] = f"Mean: {data['mean']} (Conf: {data['confidence']}, Contradiction: {data['contradiction_score']})"
            
        system_prompt = f"""You are the 'Inner Parliament' for this persona.
CONTEXT: {summary}
CLUSTERS: {json.dumps(clusters)}
TRAITS (ENACTED - DISTRIBUTIONS): {json.dumps(formatted_dists, indent=1)}
AMBIVALENCE: {json.dumps(self.ambivalence_map, indent=1)}
{policy_directive}

PERSONAL BELIEFS / SHORT ANSWERS / EMOTIONAL PROBES:
{text_context if text_context else "None provided."}

SIMULATION INSTRUCTION:
- Use <InternalThought> to resolve the conflict between what you WANT (Ideals) and what you DO (Enacted traits).
- Ground your responses in the PERSONAL BELIEFS / SHORT ANSWERS provided above.
- In Indian family scenarios, prioritize 'Dignity' and 'Harmony' but track 'Resentment' if you are forced to sacrifice Fairness.
- Follow the Stress Activation policy modifier when deciding how to act.
"""
        return {
            "prompt": system_prompt,
            "traits": distributions,
            "clusters": clusters,
            "ambivalence": self.ambivalence_map
        }

def analyze_answers(answers: Dict[str, Any]) -> Dict[str, Any]:
    engine = PersonaEngine()
    engine._seed_ideals(answers)
    engine._process_enacted(answers)
    engine._detect_contradictions()
    
    clusters = engine._calculate_clusters()
    summary = engine._generate_summary(clusters)
    
    return engine._generate_prompt(clusters, summary, answers)
