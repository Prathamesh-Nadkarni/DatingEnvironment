from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any, Optional

class ModelRole(Enum):
    FAST_INTERPRETER = "fast_interpreter"
    STRONG_INTERPRETER = "strong_interpreter"
    DIALOGUE = "dialogue"
    SECOND_OPINION = "second_opinion"
    REPORT_WRITER = "report_writer"
    EMBEDDING = "embedding"

class ModelConfig(BaseModel):
    model: str
    temperature: float = 0.0

class RouterConfig(BaseModel):
    models: Dict[ModelRole, ModelConfig]

DEFAULT_ROUTER_CONFIG = RouterConfig(
    models={
        ModelRole.FAST_INTERPRETER: ModelConfig(model="qwen3:4b", temperature=0.0),
        ModelRole.STRONG_INTERPRETER: ModelConfig(model="qwen3:8b", temperature=0.0),
        ModelRole.DIALOGUE: ModelConfig(model="qwen3:4b", temperature=0.55),
        ModelRole.SECOND_OPINION: ModelConfig(model="gemma3:4b", temperature=0.0),
        ModelRole.REPORT_WRITER: ModelConfig(model="qwen3:8b", temperature=0.2),
        ModelRole.EMBEDDING: ModelConfig(model="bge-m3", temperature=0.0),
    }
)

def get_model_for_role(role: ModelRole, config: RouterConfig = DEFAULT_ROUTER_CONFIG) -> ModelConfig:
    return config.models.get(role, ModelConfig(model="qwen3:4b", temperature=0.0))

class SemanticInteractionAnalysis(BaseModel):
    criticism: float
    contempt: float
    defensiveness: float
    stonewalling: float
    accountability: float
    validation: float
    passive_aggression: float
    confidence: float
