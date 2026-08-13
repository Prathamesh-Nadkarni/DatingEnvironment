from pydantic import BaseModel, Field
from typing import Optional

class ResourcePolicy(BaseModel):
    max_parallel_pairs: int = 1
    max_parallel_rollouts: int = 1
    max_ollama_requests: int = 1
    memory_soft_limit_mb: Optional[int] = None
    timeout_per_llm_call_s: int = 120
    max_retries: int = 2

class RunContext(BaseModel):
    seed: int
    mode: str = "quick"
    resource_policy: ResourcePolicy = Field(default_factory=ResourcePolicy)
