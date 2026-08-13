import logging
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("mirofish.fusion")

class EvidenceModality(Enum):
    STRUCTURED_RESPONSE = "structured_response"
    FREE_TEXT = "free_text"
    CONVERSATION_SAMPLE = "conversation_sample"
    VOICE_TRANSCRIPT = "voice_transcript"
    OPTIONAL_IMAGE = "optional_image"

EVIDENCE_SOURCE_WEIGHTS = {
    "sjt_action": 1.00,
    "forced_tradeoff": 0.95,
    "behavioral_ranking": 0.90,
    "structured_emotion": 0.85,
    "direct_likert": 0.75,
    "free_text_interpretation": 0.65,
    "llm_inferred": 0.55
}

class ModelAgreement(Enum):
    AGREEMENT = "AGREEMENT"
    PARTIAL_AGREEMENT = "PARTIAL_AGREEMENT"
    COMPLEMENTARY = "COMPLEMENTARY"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class FusionResult(BaseModel):
    dimension: str
    deterministic: Optional[Dict[str, Any]] = None
    primary_model: Optional[Dict[str, Any]] = None
    verifier_model: Optional[Dict[str, Any]] = None
    agreement: ModelAgreement
    fused_evidence: Optional[Dict[str, Any]] = None
    next_action: Optional[str] = None
    suggested_question_family: Optional[str] = None

class ConsensusEngine:
    def __init__(self):
        pass

    def evaluate_agreement(self, val_qwen: float, val_gemma: float) -> ModelAgreement:
        diff = abs(val_qwen - val_gemma)
        if diff < 0.15:
            return ModelAgreement.AGREEMENT
        elif diff <= 0.30:
            return ModelAgreement.PARTIAL_AGREEMENT
        elif diff <= 0.50:
            return ModelAgreement.CONFLICTING
        else:
            return ModelAgreement.CONFLICTING

    def fuse_evidence(self, dimension: str, deterministic_val: Optional[float] = None, 
                      primary_val: Optional[float] = None, verifier_val: Optional[float] = None,
                      primary_conf: float = 0.8, verifier_conf: float = 0.8) -> FusionResult:
        
        # If we have a deterministic value, it heavily overrides inferences
        if deterministic_val is not None:
            return FusionResult(
                dimension=dimension,
                deterministic={"value": deterministic_val, "confidence": 0.95},
                agreement=ModelAgreement.AGREEMENT,
                fused_evidence={"value": deterministic_val, "confidence": 0.95}
            )

        if primary_val is not None and verifier_val is not None:
            agreement = self.evaluate_agreement(primary_val, verifier_val)
            if agreement in [ModelAgreement.AGREEMENT, ModelAgreement.PARTIAL_AGREEMENT]:
                fused_val = (primary_val * primary_conf + verifier_val * verifier_conf) / (primary_conf + verifier_conf)
                fused_conf = max(primary_conf, verifier_conf) + 0.05
                return FusionResult(
                    dimension=dimension,
                    primary_model={"value": primary_val, "confidence": primary_conf},
                    verifier_model={"value": verifier_val, "confidence": verifier_conf},
                    agreement=agreement,
                    fused_evidence={"value": fused_val, "confidence": min(1.0, fused_conf)}
                )
            else:
                return FusionResult(
                    dimension=dimension,
                    primary_model={"value": primary_val, "confidence": primary_conf},
                    verifier_model={"value": verifier_val, "confidence": verifier_conf},
                    agreement=agreement,
                    fused_evidence=None,
                    next_action="ASK_DISAMBIGUATION",
                    suggested_question_family=dimension
                )
        
        if primary_val is not None:
            return FusionResult(
                dimension=dimension,
                primary_model={"value": primary_val, "confidence": primary_conf},
                agreement=ModelAgreement.INSUFFICIENT_EVIDENCE,
                fused_evidence={"value": primary_val, "confidence": primary_conf}
            )

        return FusionResult(
            dimension=dimension,
            agreement=ModelAgreement.INSUFFICIENT_EVIDENCE,
            fused_evidence=None
        )
