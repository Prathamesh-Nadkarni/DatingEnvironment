from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PairSpec(BaseModel):
    id: str
    version: int
    person_a: str
    person_b: str
    tags: List[str] = Field(default_factory=list)
    expected_dynamics: Dict[str, Any] = Field(default_factory=dict)
    directional_expectations: Dict[str, Any] = Field(default_factory=dict)
    trajectory_expectations: Dict[str, Any] = Field(default_factory=dict)
