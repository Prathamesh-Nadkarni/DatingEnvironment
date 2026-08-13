from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from synthetic_testing.enums import TestStatus

class TestReport(BaseModel):
    run_id: str
    timestamp: str
    git_commit: Optional[str] = None
    person_a: Dict[str, Any]
    person_b: Dict[str, Any]
    questionnaire_version: str
    synthesis_version: str
    simulation_version: str
    ollama: Dict[str, Any]
    mode: str
    seed: int
    
    status: TestStatus = TestStatus.FAIL
    persona_fidelity: Dict[str, Any] = Field(default_factory=dict)
    relationship_behavior: Dict[str, Any] = Field(default_factory=dict)
    causal_traces: list = Field(default_factory=list)
