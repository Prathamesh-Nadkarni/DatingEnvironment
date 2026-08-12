from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class LifePhase(str, Enum):
    NEWLYWED = "newlywed"
    CAREER_BUILDING = "career_building"
    CHILDCARE = "childcare"
    ESTABLISHED_FAMILY = "established_family"
    MIDLIFE = "midlife"

class RelationshipInjury(BaseModel):
    id: str
    type: str # e.g. "failure_to_defend", "financial_betrayal"
    victim: str # "Agent A" or "Agent B"
    severity: float # 0.0 to 1.0
    resolved: bool = False
    trust_damage: float
    resentment_growth_rate: float
    recurrence_multiplier: float = 1.5

class TraitDistribution(BaseModel):
    mean: float
    confidence: float
    evidence_count: int = 0
    contradiction_score: float = 0.0
    context_variance: float = 0.0

class PersonaContext(BaseModel):
    # Layer A: Foundation (Stored as generic dict for flexibility or mapped)
    relationship_traits: Dict[str, TraitDistribution] = Field(default_factory=dict)
    
    # Layer B: Cognitive/Emotional Properties
    self_awareness: float = 0.5
    perspective_taking: float = 0.5
    hostile_attribution_bias: float = 0.0
    benefit_of_doubt: float = 0.5
    emotional_awareness: float = 0.5
    impulse_control: float = 0.5
    feedback_receptivity: float = 0.5
    cognitive_flexibility: float = 0.5
    rumination: float = 0.0
    threat_sensitivity: float = 0.5
    accountability: float = 0.5
    ambiguity_tolerance: float = 0.5

    # Layer C: Behavioral Policies
    reactive_vs_deliberative: float = 0.5 # 0=Reactive, 1=Deliberative
    approach_vs_avoid: float = 0.5 # 0=Avoid, 1=Approach
    self_protect_vs_relationship_protect: float = 0.5 # 0=Self, 1=Relationship
    short_term_peace_vs_long_term_resolution: float = 0.5 # 0=Peace, 1=Resolution
    
    # Needs / Provision
    needs: Dict[str, float] = Field(default_factory=dict)
    provision: Dict[str, float] = Field(default_factory=dict)

class MarriageState(BaseModel):
    # Relationship Foundation
    trust_a: float = 0.5
    trust_b: float = 0.5
    emotional_safety_a: float = 0.5
    emotional_safety_b: float = 0.5
    connection: float = 0.5
    admiration_a: float = 0.5
    admiration_b: float = 0.5
    commitment_a: float = 0.5
    commitment_b: float = 0.5
    relationship_capital: float = 50.0  # 0 to 100

    # Negative Accumulated State
    resentment_a: float = 0.0
    resentment_b: float = 0.0
    burnout_a: float = 0.0
    burnout_b: float = 0.0
    unresolved_hurt_a: float = 0.0
    unresolved_hurt_b: float = 0.0

    # Individual Happiness & Needs
    happiness_a: float = 0.5
    happiness_b: float = 0.5
    need_fulfillment_a: float = 0.5
    need_fulfillment_b: float = 0.5

    # Structural Factors
    financial_stability: float = 0.5
    intimacy_satisfaction_a: float = 0.5
    intimacy_satisfaction_b: float = 0.5
    family_boundary_health: float = 0.5
    fairness_a: float = 0.5
    fairness_b: float = 0.5

    # Timeline & History
    marriage_month: int = 0
    injuries: List[RelationshipInjury] = Field(default_factory=list)
    successful_repairs: int = 0
    exit_barriers: float = 0.5 # e.g. children, financial dependence, family pressure
    
    @property
    def current_life_phase(self) -> LifePhase:
        if self.marriage_month < 24:
            return LifePhase.NEWLYWED
        elif self.marriage_month < 60:
            return LifePhase.CAREER_BUILDING
        elif self.marriage_month < 120:
            return LifePhase.CHILDCARE
        elif self.marriage_month < 240:
            return LifePhase.ESTABLISHED_FAMILY
        else:
            return LifePhase.MIDLIFE
    
    def get_happiness(self, agent_id: str) -> float:
        """Returns the individual happiness for the specified agent (Agent A or Agent B)."""
        is_a = agent_id == "Agent A"
        safety = self.emotional_safety_a if is_a else self.emotional_safety_b
        needs = self.need_fulfillment_a if is_a else self.need_fulfillment_b
        trust = self.trust_a if is_a else self.trust_b
        fairness = self.fairness_a if is_a else self.fairness_b
        intimacy = self.intimacy_satisfaction_a if is_a else self.intimacy_satisfaction_b
        resentment = self.resentment_a if is_a else self.resentment_b
        burnout = self.burnout_a if is_a else self.burnout_b
        
        # Empirical Tuning (Phase 1 V4): Gottman ratio suggests negative sentiment overrides positives heavily.
        happiness = (
            0.20 * safety
            + 0.15 * needs
            + 0.15 * self.connection
            + 0.20 * trust
            + 0.15 * fairness
            + 0.15 * intimacy
            - 0.50 * resentment  # Strong Gottman penalty for contempt/resentment
            - 0.25 * burnout     # High penalty for burnout/exhaustion
        )
        return max(0.0, min(1.0, happiness))
        
    def update_happiness(self):
        """Updates internal happiness variables."""
        self.happiness_a = self.get_happiness("Agent A")
        self.happiness_b = self.get_happiness("Agent B")
        
    def apply_event_impact(self, event_type: str, severity: float):
        """Applies generic life events to the relationship state."""
        # This is a placeholder for the logic in V3. 
        # In V2, scenarios will explicitly target state variables.
        pass
        
    def trigger_injury(self, victim: str, injury_type: str, base_severity: float) -> float:
        """Creates or compounds an injury, returning the effective severity."""
        # Find unresolved injuries of the same type
        prior = [i for i in self.injuries if i.victim == victim and i.type == injury_type and not i.resolved]
        
        effective_severity = base_severity
        if prior:
            # Compound severity
            last_injury = prior[-1]
            effective_severity += last_injury.severity * last_injury.recurrence_multiplier
            
        new_injury = RelationshipInjury(
            id=f"{injury_type}_{self.marriage_month}",
            type=injury_type,
            victim=victim,
            severity=effective_severity,
            trust_damage=effective_severity * 0.2,
            resentment_growth_rate=effective_severity * 0.05
        )
        self.injuries.append(new_injury)
        
        # Immediate effects
        if victim == "Agent A":
            self.trust_a = max(0.0, self.trust_a - new_injury.trust_damage)
            self.unresolved_hurt_a += effective_severity * 0.5
        else:
            self.trust_b = max(0.0, self.trust_b - new_injury.trust_damage)
            self.unresolved_hurt_b += effective_severity * 0.5
            
        # Capital takes a hit
        damage_to_capital = (effective_severity * 10) * (1 - (self.relationship_capital / 200)) # Capital protects itself
        self.relationship_capital = max(0.0, self.relationship_capital - damage_to_capital)
        
        self.update_happiness()
        return effective_severity
        
    def repair_injury(self, victim: str, injury_type: str, repair_effectiveness: float):
        """Attempts to repair active injuries."""
        active = [i for i in self.injuries if i.victim == victim and i.type == injury_type and not i.resolved]
        
        for injury in active:
            if repair_effectiveness > injury.severity * 0.8: # Must be a strong repair to resolve
                injury.resolved = True
                self.successful_repairs += 1
                
                # Restore some trust
                if victim == "Agent A":
                    self.trust_a = min(1.0, self.trust_a + (injury.trust_damage * 0.5))
                    self.unresolved_hurt_a = max(0.0, self.unresolved_hurt_a - injury.severity * 0.5)
                else:
                    self.trust_b = min(1.0, self.trust_b + (injury.trust_damage * 0.5))
                    self.unresolved_hurt_b = max(0.0, self.unresolved_hurt_b - injury.severity * 0.5)
                    
                # Restore capital
                self.relationship_capital = min(100.0, self.relationship_capital + 5.0)
                
        self.update_happiness()
