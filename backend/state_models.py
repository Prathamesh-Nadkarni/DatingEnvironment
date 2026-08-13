from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class LifePhase(str, Enum):
    NEWLYWED = "newlywed"
    CAREER_BUILDING = "career_building"
    CHILDCARE = "childcare"
    ESTABLISHED_FAMILY = "established_family"
    MIDLIFE = "midlife"
    DUAL_CAREGIVING = "dual_caregiving"
    MATURE_PARTNERSHIP = "mature_partnership"

    @classmethod
    def for_year(cls, year: int) -> "LifePhase":
        """Return the 25-year life phase used by the annual scenario planner."""
        if year <= 2:
            return cls.NEWLYWED
        if year <= 5:
            return cls.CAREER_BUILDING
        if year <= 9:
            return cls.CHILDCARE
        if year <= 13:
            return cls.ESTABLISHED_FAMILY
        if year <= 17:
            return cls.MIDLIFE
        if year <= 21:
            return cls.DUAL_CAREGIVING
        return cls.MATURE_PARTNERSHIP

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
    variance: float = 0.0
    contradiction_score: float = 0.0
    context_dependence: float = 0.0

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
    connection_a: float = 0.5
    connection_b: float = 0.5
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

    # Individual Needs
    need_fulfillment_a: float = 0.5
    need_fulfillment_b: float = 0.5

    # Structural Factors
    financial_stability: float = 0.5
    intimacy_satisfaction_a: float = 0.5
    intimacy_satisfaction_b: float = 0.5
    family_boundary_health: float = 0.5
    perceived_fairness_a: float = 0.5
    perceived_fairness_b: float = 0.5
    feeling_heard_a: float = 0.5
    feeling_heard_b: float = 0.5

    # Timeline & History
    marriage_month: int = 0
    injuries: List[RelationshipInjury] = Field(default_factory=list)
    successful_repairs: int = 0
    exit_barriers: float = 0.5 # e.g. children, financial dependence, family pressure
    
    @property
    def current_life_phase(self) -> LifePhase:
        year = max(1, (self.marriage_month + 11) // 12)
        return LifePhase.for_year(year)
    
    @property
    def happiness_a(self) -> float:
        return self.get_happiness("Agent A")
        
    @property
    def happiness_b(self) -> float:
        return self.get_happiness("Agent B")

    def get_happiness(self, agent_id: str) -> float:
        """Computes the individual happiness for the specified agent."""
        is_a = agent_id == "Agent A"
        safety = self.emotional_safety_a if is_a else self.emotional_safety_b
        needs = self.need_fulfillment_a if is_a else self.need_fulfillment_b
        trust = self.trust_a if is_a else self.trust_b
        fairness = self.perceived_fairness_a if is_a else self.perceived_fairness_b
        intimacy = self.intimacy_satisfaction_a if is_a else self.intimacy_satisfaction_b
        resentment = self.resentment_a if is_a else self.resentment_b
        burnout = self.burnout_a if is_a else self.burnout_b
        connection = self.connection_a if is_a else self.connection_b
        
        # Happiness as an emergent property of state
        happiness = (
            0.20 * safety
            + 0.15 * needs
            + 0.15 * connection
            + 0.20 * trust
            + 0.15 * fairness
            + 0.15 * intimacy
            - 0.50 * resentment
            - 0.25 * burnout
        )
        return max(0.0, min(1.0, happiness))
        
    def update_happiness(self):
        """Deprecated: Happiness is now a computed property."""
        pass
        
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
        effective_severity = max(0.0, min(1.0, effective_severity))
            
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
        active = [
            i for i in self.injuries
            if i.victim == victim and i.type == injury_type and not i.resolved
        ]

        for injury in active:
            if repair_effectiveness > injury.severity * 0.8:
                injury.resolved = True
                self.successful_repairs += 1

                if victim == "Agent A":
                    self.trust_a = min(1.0, self.trust_a + (injury.trust_damage * 0.5))
                    self.unresolved_hurt_a = max(
                        0.0, self.unresolved_hurt_a - injury.severity * 0.5
                    )
                else:
                    self.trust_b = min(1.0, self.trust_b + (injury.trust_damage * 0.5))
                    self.unresolved_hurt_b = max(
                        0.0, self.unresolved_hurt_b - injury.severity * 0.5
                    )

                self.relationship_capital = min(100.0, self.relationship_capital + 5.0)

        self.update_happiness()


# ---------------------------------------------------------------------------
# Persistent world and relationship-narrative state for the longitudinal
# simulator.  These models intentionally remain separate from MarriageState:
# LifeState stores objective facts, while NarrativeState stores beliefs each
# partner has formed about the relationship.
# ---------------------------------------------------------------------------


class ResidenceState(BaseModel):
    arrangement: str = "independent_rental"
    ownership: str = "renting"
    region: str = "urban"
    stability: float = 0.7


class CareerState(BaseModel):
    employed: bool = True
    level: str = "early_career"
    workload: float = 0.5
    satisfaction: float = 0.5
    income_units: float = 1.0
    relocation_possible: bool = True


class FinancialState(BaseModel):
    savings_units: float = 1.0
    debt_units: float = 0.0
    stability: float = 0.6
    finances_joint: bool = True
    hidden_obligations: bool = False


class ChildState(BaseModel):
    id: str
    age: int = 0
    health: float = 1.0
    living_at_home: bool = True


class ParentState(BaseModel):
    id: str
    side: str
    alive: bool = True
    health: float = 0.8
    financial_dependency: float = 0.2
    lives_with_couple: bool = False


class HealthState(BaseModel):
    health: float = 0.9
    chronic_condition: bool = False
    caregiving_load: float = 0.0


class LifeState(BaseModel):
    """Objective facts that determine whether a scenario can occur."""

    year: int = 1
    residence: ResidenceState = Field(default_factory=ResidenceState)
    career_a: CareerState = Field(default_factory=CareerState)
    career_b: CareerState = Field(default_factory=CareerState)
    finances: FinancialState = Field(default_factory=FinancialState)
    children: List[ChildState] = Field(default_factory=list)
    parents_a: List[ParentState] = Field(
        default_factory=lambda: [ParentState(id="parent_a_1", side="a")]
    )
    parents_b: List[ParentState] = Field(
        default_factory=lambda: [ParentState(id="parent_b_1", side="b")]
    )
    health_a: HealthState = Field(default_factory=HealthState)
    health_b: HealthState = Field(default_factory=HealthState)
    family_network: Dict[str, Any] = Field(
        default_factory=lambda: {"has_sibling_a": True, "has_sibling_b": True}
    )
    social_network: Dict[str, Any] = Field(default_factory=dict)
    plans: Dict[str, Any] = Field(
        default_factory=lambda: {"children_intent": "open", "retirement_age": 65}
    )
    flags: List[str] = Field(default_factory=list)

    @property
    def phase(self) -> LifePhase:
        return LifePhase.for_year(self.year)

    @property
    def has_children(self) -> bool:
        return bool(self.children)

    def advance_year(self) -> None:
        self.year += 1
        for child in self.children:
            child.age += 1


class PartnerNarrative(BaseModel):
    feels_prioritized: float = 0.5
    partner_is_reliable: float = 0.5
    partner_understands_me: float = 0.5
    partner_defends_me: float = 0.5
    partner_is_fair: float = 0.5
    conflict_is_repairable: float = 0.5
    relationship_is_safe: float = 0.5

    def apply_delta(self, field_name: str, delta: float) -> None:
        if not hasattr(self, field_name):
            return
        current = float(getattr(self, field_name))
        setattr(self, field_name, max(0.0, min(1.0, current + delta)))


class NarrativeState(BaseModel):
    partner_a: PartnerNarrative = Field(default_factory=PartnerNarrative)
    partner_b: PartnerNarrative = Field(default_factory=PartnerNarrative)
    active_narratives: List[str] = Field(default_factory=list)


class ScenarioHistoryRecord(BaseModel):
    scenario_id: str
    family_id: str
    year: int
    primary_domain: str
    severity: float
    outcome: str
    memory_tags: List[str] = Field(default_factory=list)
    activated_followups: List[str] = Field(default_factory=list)


class YearSnapshot(BaseModel):
    year: int
    scenarios_experienced: int
    happiness_a: float
    happiness_b: float
    trust_a: float
    trust_b: float
    resentment_a: float
    resentment_b: float
    connection: float
    relationship_capital: float
    new_injuries: int = 0
    repaired_injuries: int = 0
    active_narratives: List[str] = Field(default_factory=list)
