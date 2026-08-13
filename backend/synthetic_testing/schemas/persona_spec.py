from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from synthetic_testing.enums import PersonaConsistencyMode

class PersonaValues(BaseModel):
    egalitarianism: float = 0.5
    commitment: float = 0.5
    family_loyalty: float = 0.5

class PersonaNeeds(BaseModel):
    reassurance: float = 0.5
    emotional_closeness: float = 0.5
    autonomy: float = 0.5
    affection: float = 0.5

class PersonaCognition(BaseModel):
    rejection_sensitivity: float = 0.5
    hostile_attribution_bias: float = 0.5
    catastrophizing: float = 0.5
    perspective_taking: float = 0.5
    self_awareness: float = 0.5

class PersonaEmotion(BaseModel):
    anxiety_activation: float = 0.5
    anger_activation: float = 0.5
    shame_activation: float = 0.5
    recovery_speed: float = 0.5

class PersonaBehavior(BaseModel):
    withdrawal_tendency: float = 0.5
    reassurance_seeking: float = 0.5
    repair_skill: float = 0.5

class PersonaAdaptation(BaseModel):
    feedback_receptivity: float = 0.5
    learning_rate: float = 0.5

class GroundTruth(BaseModel):
    values: PersonaValues = Field(default_factory=PersonaValues)
    needs: PersonaNeeds = Field(default_factory=PersonaNeeds)
    cognition: PersonaCognition = Field(default_factory=PersonaCognition)
    emotion: PersonaEmotion = Field(default_factory=PersonaEmotion)
    behavior: PersonaBehavior = Field(default_factory=PersonaBehavior)
    adaptation: PersonaAdaptation = Field(default_factory=PersonaAdaptation)

class SyntheticPersonaSpec(BaseModel):
    id: str
    version: int
    display_name: str
    tags: List[str] = Field(default_factory=list)
    consistency_mode: PersonaConsistencyMode = PersonaConsistencyMode.CLEAN
    ground_truth: GroundTruth
    ollama_behavioral_brief: str
