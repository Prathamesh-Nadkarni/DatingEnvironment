"""Adaptive, evidence-led routing over the approved intake question bank.

The router deliberately selects only questions registered in ``INTAKE_SECTIONS``
or the small, reviewed resolver bank below.  An LLM may interpret free text,
but it never invents production questions or assigns final trait scores.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set

try:
    from .intake_questions import INTAKE_SECTIONS
    from .persona_synthesis import CORE_DIMENSIONS, MAPPING_TABLE, SCALE_MAPPINGS
except ImportError:
    from intake_questions import INTAKE_SECTIONS
    from persona_synthesis import CORE_DIMENSIONS, MAPPING_TABLE, SCALE_MAPPINGS


class QuestionType(str, Enum):
    LIKERT = "likert"
    FORCED_CHOICE = "forced_choice"
    MULTI_CHOICE = "multi_choice"
    RANKING = "ranking"
    RESOURCE_ALLOCATION = "resource_allocation"
    SJT = "situational_judgment"
    EMOTION_PROBE = "emotion_probe"
    IMPULSE_PROBE = "impulse_probe"
    REFLECTION = "reflection"
    ADAPTATION_PROBE = "adaptation_probe"
    FREE_TEXT = "free_text"
    THRESHOLD = "threshold"


@dataclass(frozen=True)
class DomainBudget:
    minimum_questions: int = 3
    target_questions: int = 7
    maximum_questions: int = 16


@dataclass
class AdaptiveIntakeState:
    answers: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    asked_question_ids: Set[str] = field(default_factory=set)
    asked_question_order: List[str] = field(default_factory=list)
    domain_counts: Dict[str, int] = field(default_factory=dict)
    type_counts: Dict[str, int] = field(default_factory=dict)
    trait_distributions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    contradiction_scores: Dict[str, float] = field(default_factory=dict)
    context_coverage: Dict[str, Set[str]] = field(default_factory=dict)
    fatigue_score: float = 0.0
    question_count: int = 0
    screen_count: int = 0

    @classmethod
    def from_session(cls, session_role: Dict[str, Any]) -> "AdaptiveIntakeState":
        raw = session_role.get("adaptive_intake", {})
        return cls(
            answers=dict(session_role.get("answers", raw.get("answers", {}))),
            evidence=list(raw.get("evidence", session_role.get("evidence_log", []))),
            asked_question_ids=set(raw.get("asked_question_ids", session_role.get("answers", {}).keys())),
            asked_question_order=list(raw.get("asked_question_order", session_role.get("answers", {}).keys())),
            domain_counts=dict(raw.get("domain_counts", {})),
            type_counts=dict(raw.get("type_counts", {})),
            trait_distributions=dict(raw.get("trait_distributions", {})),
            contradiction_scores=dict(raw.get("contradiction_scores", {})),
            context_coverage={key: set(value) for key, value in raw.get("context_coverage", {}).items()},
            fatigue_score=float(raw.get("fatigue_score", 0.0)),
            question_count=int(raw.get("question_count", len(session_role.get("answers", {})))),
            screen_count=int(raw.get("screen_count", 0)),
        )

    def to_session(self) -> Dict[str, Any]:
        return {
            "evidence": self.evidence,
            "asked_question_ids": sorted(self.asked_question_ids),
            "asked_question_order": self.asked_question_order,
            "domain_counts": self.domain_counts,
            "type_counts": self.type_counts,
            "trait_distributions": self.trait_distributions,
            "contradiction_scores": self.contradiction_scores,
            "context_coverage": {key: sorted(value) for key, value in self.context_coverage.items()},
            "fatigue_score": round(self.fatigue_score, 3),
            "question_count": self.question_count,
            "screen_count": self.screen_count,
        }


SECTION_DOMAINS = {
    "Initial Match Intent Screener": "life_goals",
    "Background and Life Context": "family_of_origin",
    "Core Values and Identity Priorities": "adaptability_growth",
    "Marriage Philosophy and Couple Identity": "commitment_loyalty",
    "Family Boundaries and Parental Involvement": "in_laws_extended_family",
    "Gender Roles and Domestic Labor": "household_fairness",
    "Financial Philosophy and Mutuality": "money_financial_psychology",
    "Conflict Style and Repair Behavior": "conflict_repair",
    "Emotional Needs and Co-Regulation": "emotional_needs",
    "Tradition, Religion, and Community": "religion_culture_tradition",
    "Food, Lifestyle, and Home Culture": "lifestyle_habits",
    "Social Image, Shame, and Public Respect": "social_life_friendships",
    "Career, Ambition, and Sacrifice": "career_ambition",
    "Parenting and Children": "parenting_children",
    "Eldercare and Family Duty": "health_caregiving",
    "Autonomy, Privacy, and Personal Space": "autonomy_privacy",
    "Trust, Jealousy, and Loyalty": "trust_jealousy",
    "Commitment, Forgiveness, and Exit Thresholds": "commitment_loyalty",
    "Emotional Regulation and Stress Response": "emotional_regulation",
    "Power, Control, and Safety": "power_control_safety",
    "Adaptability, Reflection, and Growth": "adaptability_growth",
    "Sex, Affection, and Intimacy": "sex_affection_intimacy",
}


TYPE_BY_FORMAT = {
    "scale_6": QuestionType.LIKERT,
    "scale_7": QuestionType.LIKERT,
    "importance_scale": QuestionType.LIKERT,
    "forced_choice": QuestionType.FORCED_CHOICE,
    "multiple_choice": QuestionType.MULTI_CHOICE,
    "ranking": QuestionType.RANKING,
    "sjt": QuestionType.SJT,
    "probe_group": QuestionType.SJT,
    "short_answer": QuestionType.FREE_TEXT,
    "text_input": QuestionType.FREE_TEXT,
}


TRAIT_IMPORTANCE = {
    trait: 0.75 for trait in CORE_DIMENSIONS
}
TRAIT_IMPORTANCE.update({
    "partner_advocacy": 1.0, "boundary_strength": 1.0,
    "repair_skill": 1.0, "co_regulation_capacity": 1.0,
    "financial_mutuality": 0.95, "family_deference": 0.95,
    "jealousy_threshold": 0.9, "caregiving_flexibility": 0.9,
    "parenting_alignment": 0.9, "burnout_vulnerability": 0.9,
})


RESOLVER_QUESTIONS = [
    {
        "id": "AR.FAMILY_ADVOCACY_01", "section_name": "Adaptive Clarification",
        "domain": "in_laws_extended_family", "format": "sjt",
        "question_type": QuestionType.ADAPTATION_PROBE.value,
        "text": "You said protecting a spouse matters, but you also prefer to avoid public conflict. What would most likely stop you from speaking up when a parent criticizes your spouse?",
        "options": ["Fear of escalating the moment", "Fear of embarrassing my parent", "I would not know whether my spouse wanted intervention", "Respect for elders", "I might agree with the criticism"],
        "targets": ["partner_advocacy", "family_deference", "public_harmony_preference"],
        "diagnostic_value": 0.9, "evidence_family": "family_advocacy_resolver",
        "contexts": ["parents", "public_conflict"], "minimum_spacing": 10,
        "contradiction_resolver_for": ["partner_advocacy", "family_deference"],
    },
    {
        "id": "AR.TRUST_AUTONOMY_01", "section_name": "Adaptive Clarification",
        "domain": "trust_jealousy", "format": "sjt",
        "question_type": QuestionType.ADAPTATION_PROBE.value,
        "text": "You value independence. If a partner declined to share live location during a trip with friends, what would you most likely infer?",
        "options": ["Nothing concerning", "They value privacy", "I would ask for reassurance", "I would worry they were hiding something", "I would insist because partners should always share it"],
        "targets": ["autonomy_need", "jealousy_threshold", "privacy_need"],
        "diagnostic_value": 0.9, "evidence_family": "trust_autonomy_resolver",
        "contexts": ["friends", "privacy"], "minimum_spacing": 10,
        "contradiction_resolver_for": ["autonomy_need", "jealousy_threshold"],
    },
    {
        "id": "AR.REPAIR_01", "section_name": "Adaptive Clarification",
        "domain": "conflict_repair", "format": "adaptation_probe",
        "question_type": QuestionType.ADAPTATION_PROBE.value,
        "text": "After repeating the same conflict, what would make you change your approach next time?",
        "options": ["Seeing that my partner is truly hurt", "A clear practical agreement", "Time and distance", "Nothing; they should change first", "Advice from someone I trust"],
        "targets": ["repair_skill", "accountability", "forgiveness_rate"],
        "diagnostic_value": 0.86, "evidence_family": "repair_adaptation_resolver",
        "contexts": ["private_conflict"], "minimum_spacing": 8,
        "contradiction_resolver_for": ["repair_skill"],
    },
]


class AdaptiveQuestionRouter:
    core_screen_target = 72
    minimum_questions = 150
    maximum_questions = 250
    resolution_threshold = 0.80

    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)
        self.question_bank = self._build_question_bank()
        self.questions_by_id = {question["id"]: question for question in self.question_bank}
        self.domain_budgets = defaultdict(DomainBudget)
        self.core_question_ids = self._select_core_screen()

    def _build_question_bank(self) -> List[Dict[str, Any]]:
        bank: List[Dict[str, Any]] = []
        for section in INTAKE_SECTIONS:
            domain = SECTION_DOMAINS.get(section.get("section"), "adaptability_growth")
            for question in section.get("questions", []):
                item = dict(question)
                question_type = TYPE_BY_FORMAT.get(item.get("format"), QuestionType.MULTI_CHOICE)
                targets = self._targets_for_question(item)
                item.update({
                    "section_name": section.get("section", "General"),
                    "domain": domain,
                    "question_type": question_type.value,
                    "targets": targets,
                    "contexts": self._contexts_for_question(item, domain),
                    "evidence_family": f"{domain}:{item['id'].split('.')[0]}",
                    "diagnostic_value": self._diagnostic_value(question_type, targets),
                    "minimum_spacing": 3 if question_type == QuestionType.FREE_TEXT else 2,
                    "transparency": "low" if question_type in {QuestionType.SJT, QuestionType.FORCED_CHOICE} else "medium",
                })
                bank.append(item)
        bank.extend(RESOLVER_QUESTIONS)
        return bank

    @staticmethod
    def _targets_for_question(question: Dict[str, Any]) -> List[str]:
        question_id = question["id"]
        targets: Set[str] = set()
        mapping = MAPPING_TABLE.get(question_id)
        if isinstance(mapping, dict):
            for effect in mapping.values():
                if isinstance(effect, dict):
                    targets.update(effect.keys())
        targets.update(SCALE_MAPPINGS.get(question_id, {}).keys())
        return sorted(target for target in targets if target in CORE_DIMENSIONS)

    @staticmethod
    def _contexts_for_question(question: Dict[str, Any], domain: str) -> List[str]:
        text = question.get("text", "").lower()
        contexts = [domain]
        for label, tokens in {
            "parents": ("parent", "elder", "in-law", "relative"),
            "public_conflict": ("public", "family", "community"),
            "career": ("career", "work", "job"),
            "money": ("money", "expense", "financial", "rupee"),
            "children": ("child", "parenting", "birth"),
            "intimacy": ("sex", "affection", "intimacy"),
        }.items():
            if any(token in text for token in tokens):
                contexts.append(label)
        return contexts

    @staticmethod
    def _diagnostic_value(question_type: QuestionType, targets: List[str]) -> float:
        type_weight = {
            QuestionType.SJT: 0.88, QuestionType.FORCED_CHOICE: 0.80,
            QuestionType.RANKING: 0.78, QuestionType.LIKERT: 0.62,
            QuestionType.FREE_TEXT: 0.72, QuestionType.MULTI_CHOICE: 0.65,
        }.get(question_type, 0.65)
        return min(0.95, type_weight + min(0.08, len(targets) * 0.025))

    def _select_core_screen(self) -> List[str]:
        """A 72-item broad screen, distributed across the existing domains."""
        chosen: List[str] = []
        by_domain: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for question in self.question_bank:
            if not question["id"].startswith("AR.") and question["id"] not in {"0.1", "0.2", "0.3", "0.4"}:
                by_domain[question["domain"]].append(question)
        preferred_types = [QuestionType.SJT.value, QuestionType.FORCED_CHOICE.value, QuestionType.LIKERT.value]
        while len(chosen) < self.core_screen_target:
            progressed = False
            for domain in sorted(by_domain):
                candidates = [q for q in by_domain[domain] if q["id"] not in chosen]
                if not candidates:
                    continue
                seen_types = {self.questions_by_id[qid]["question_type"] for qid in chosen if self.questions_by_id[qid]["domain"] == domain}
                candidates.sort(key=lambda q: (
                    q["question_type"] in seen_types,
                    preferred_types.index(q["question_type"]) if q["question_type"] in preferred_types else 9,
                    -q["diagnostic_value"],
                ))
                chosen.append(candidates[0]["id"])
                progressed = True
                if len(chosen) >= self.core_screen_target:
                    break
            if not progressed:
                break
        return chosen

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        return self.questions_by_id.get(question_id)

    def update_state(self, state: AdaptiveIntakeState, question_id: str, answer: Any) -> AdaptiveIntakeState:
        question = self.get_question_by_id(question_id)
        if not question or question_id in state.asked_question_ids:
            return state
        state.answers[question_id] = answer
        state.asked_question_ids.add(question_id)
        state.asked_question_order.append(question_id)
        state.question_count += 1
        if question_id in self.core_question_ids:
            state.screen_count += 1
        domain = question["domain"]
        state.domain_counts[domain] = state.domain_counts.get(domain, 0) + 1
        question_type = question["question_type"]
        state.type_counts[question_type] = state.type_counts.get(question_type, 0) + 1
        state.fatigue_score = min(1.0, state.question_count / self.maximum_questions)
        state.evidence.extend(self.extract_deterministic_evidence(question, answer))
        self._refresh_distributions(state)
        return state

    def add_model_evidence(
        self,
        state: AdaptiveIntakeState,
        question_id: str,
        trait_evidence: Iterable[Dict[str, Any]],
        confidence: float,
    ) -> None:
        """Add validated LLM extraction as lower-weight evidence, never a final score."""
        question = self.get_question_by_id(question_id)
        if not question:
            return
        for signal in trait_evidence:
            trait = signal.get("trait")
            try:
                value = float(signal.get("value"))
            except (TypeError, ValueError):
                continue
            if trait not in CORE_DIMENSIONS or not 0.0 <= value <= 1.0:
                continue
            entry = self._evidence(question, trait, value, max(0.15, min(0.55, confidence * 0.55)))
            entry["source"] = "llm_structured_extraction"
            state.evidence.append(entry)
        self._refresh_distributions(state)

    def extract_deterministic_evidence(self, question: Dict[str, Any], answer: Any) -> List[Dict[str, Any]]:
        """Map approved structured responses into evidence; no LLM scoring."""
        question_id = question["id"]
        action = answer.get("action") if isinstance(answer, dict) else answer
        if isinstance(action, dict):
            action = action.get("id", action.get("text"))
        if isinstance(action, list):
            # Rankings and allocations are retained as raw evidence until they
            # receive a reviewed deterministic mapping.
            action = None
        evidence: List[Dict[str, Any]] = []
        mapping = MAPPING_TABLE.get(question_id, {})
        if isinstance(mapping, dict) and action in mapping:
            for trait, shift in mapping[action].items():
                evidence.append(self._evidence(question, trait, 0.5 + float(shift), abs(float(shift)) + 0.2))
        if question_id in SCALE_MAPPINGS:
            try:
                normalized = (float(action) - 1.0) / 6.0
            except (TypeError, ValueError):
                normalized = None
            if normalized is not None:
                for trait, direction in SCALE_MAPPINGS[question_id].items():
                    value = normalized if direction > 0 else 1.0 - normalized
                    evidence.append(self._evidence(question, trait, value, 0.65))
        return evidence

    @staticmethod
    def _evidence(question: Dict[str, Any], trait: str, value: float, weight: float) -> Dict[str, Any]:
        return {
            "trait": trait, "value": max(0.0, min(1.0, value)),
            "weight": weight, "source_question": question["id"],
            "evidence_family": question["evidence_family"],
            "question_type": question["question_type"],
            "contexts": question["contexts"],
            "source": "deterministic_structured_mapping",
        }

    def _refresh_distributions(self, state: AdaptiveIntakeState) -> None:
        by_trait: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for evidence in state.evidence:
            if evidence.get("trait") in CORE_DIMENSIONS and "value" in evidence:
                by_trait[evidence["trait"]].append(evidence)
        distributions: Dict[str, Dict[str, float]] = {}
        contexts: Dict[str, Set[str]] = defaultdict(set)
        for trait in CORE_DIMENSIONS:
            entries = by_trait.get(trait, [])
            if not entries:
                distributions[trait] = {"mean": 0.5, "confidence": 0.05, "variance": 0.12, "contradiction_score": 0.0, "context_dependence": 0.0, "evidence_count": 0}
                continue
            family_seen: Counter[str] = Counter()
            weighted = []
            for entry in entries:
                family_seen[entry["evidence_family"]] += 1
                discount = (1.0, 0.60, 0.40)[min(2, family_seen[entry["evidence_family"]] - 1)]
                effective_weight = entry["weight"] * discount
                weighted.append((entry, effective_weight))
                contexts[trait].update(entry.get("contexts", []))
            total_weight = sum(weight for _, weight in weighted)
            mean = sum(entry["value"] * weight for entry, weight in weighted) / total_weight
            variance = sum(weight * (entry["value"] - mean) ** 2 for entry, weight in weighted) / total_weight
            independent_families = len(family_seen)
            type_diversity = len({entry["question_type"] for entry, _ in weighted})
            context_diversity = len(contexts[trait])
            confidence = min(0.95, 0.10 + independent_families * 0.13 + type_diversity * 0.08 + min(0.12, context_diversity * 0.03))
            same_context_values: Dict[str, List[float]] = defaultdict(list)
            for entry, _ in weighted:
                same_context_values["|".join(sorted(entry.get("contexts", [])))].append(entry["value"])
            within_context_variance = max((self._variance(values) for values in same_context_values.values()), default=0.0)
            contradiction = min(1.0, within_context_variance * 4.0)
            context_dependence = min(1.0, max(0.0, variance * 4.0 - contradiction * 0.3))
            distributions[trait] = {
                "mean": round(mean, 3), "confidence": round(confidence * (1 - contradiction * 0.35), 3),
                "variance": round(variance, 3), "contradiction_score": round(contradiction, 3),
                "context_dependence": round(context_dependence, 3), "evidence_count": len(entries),
            }
        state.trait_distributions = distributions
        state.contradiction_scores = {trait: data["contradiction_score"] for trait, data in distributions.items()}
        state.context_coverage = contexts

    @staticmethod
    def _variance(values: Iterable[float]) -> float:
        values = list(values)
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((value - mean) ** 2 for value in values) / len(values)

    def should_stop(self, state: AdaptiveIntakeState) -> bool:
        if state.question_count >= self.maximum_questions:
            return True
        if state.question_count < self.minimum_questions:
            return False
        critical = [trait for trait, importance in TRAIT_IMPORTANCE.items() if importance >= 0.9]
        resolved = all(state.trait_distributions.get(trait, {}).get("confidence", 0.0) >= self.resolution_threshold for trait in critical)
        contradictions_resolved = all(state.contradiction_scores.get(trait, 0.0) < 0.20 for trait in critical)
        coverage_complete = all(state.domain_counts.get(domain, 0) >= budget.minimum_questions for domain, budget in self.domain_budgets.items())
        # Only require coverage for domains that are actually represented in this bank.
        represented = {question["domain"] for question in self.question_bank if not question["id"].startswith("AR.")}
        coverage_complete = all(state.domain_counts.get(domain, 0) >= self.domain_budgets[domain].minimum_questions for domain in represented)
        return resolved and contradictions_resolved and coverage_complete

    def get_progress(self, state: AdaptiveIntakeState) -> Dict[str, Any]:
        return {
            "question_count": state.question_count,
            "core_screen_complete": state.screen_count >= len(self.core_question_ids),
            "phase": "core_profile" if state.screen_count < len(self.core_question_ids) else "adaptive_deepening",
            "remaining_unresolved_traits": [
                trait for trait, data in state.trait_distributions.items()
                if data.get("confidence", 0.0) < self.resolution_threshold or data.get("contradiction_score", 0.0) >= 0.20
            ][:8],
            "complete": self.should_stop(state),
            "minimum_questions": self.minimum_questions,
            "maximum_questions": self.maximum_questions,
        }

    def get_next_question(self, answers: Dict[str, Any], evidence_store_state: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Compatibility wrapper retained for existing callers."""
        state = AdaptiveIntakeState(answers=dict(answers))
        if evidence_store_state:
            state = AdaptiveIntakeState.from_session({"answers": answers, "adaptive_intake": evidence_store_state})
        return self.select_next(state)

    def select_next(self, state: AdaptiveIntakeState) -> Optional[Dict[str, Any]]:
        if self.should_stop(state):
            return None
        core_remaining = [question_id for question_id in self.core_question_ids if question_id not in state.asked_question_ids]
        if core_remaining:
            return self.questions_by_id[core_remaining[0]]
        candidates = [question for question in self.question_bank if self._eligible(question, state)]
        if not candidates:
            return None
        scored = [(question, self._score(question, state)) for question in candidates]
        scored = [(question, score) for question, score in scored if score > 0]
        if not scored:
            return None
        scored.sort(key=lambda item: item[1], reverse=True)
        top = scored[:10]
        weights = [score for _, score in top]
        return self.random.choices([question for question, _ in top], weights=weights, k=1)[0]

    def _eligible(self, question: Dict[str, Any], state: AdaptiveIntakeState) -> bool:
        if question["id"] in state.asked_question_ids:
            return False
        domain = question["domain"]
        budget = self.domain_budgets[domain]
        if state.domain_counts.get(domain, 0) >= budget.maximum_questions:
            return False
        recent_domains = [
            self.questions_by_id[qid]["domain"] for qid in state.asked_question_order[-3:]
            if qid in self.questions_by_id
        ]
        if recent_domains.count(domain) >= 2 and state.domain_counts.get(domain, 0) >= budget.minimum_questions:
            return False
        return True

    def _score(self, question: Dict[str, Any], state: AdaptiveIntakeState) -> float:
        domain = question["domain"]
        domain_count = state.domain_counts.get(domain, 0)
        budget = self.domain_budgets[domain]
        coverage_need = 1.7 if domain_count < budget.minimum_questions else max(0.55, budget.target_questions / max(1, domain_count + 1))
        trait_needs = []
        for trait in question["targets"]:
            distribution = state.trait_distributions.get(trait, {})
            uncertainty = 1.0 - distribution.get("confidence", 0.05)
            contradiction = distribution.get("contradiction_score", 0.0)
            context_gap = max(0.0, 1.0 - min(1.0, len(state.context_coverage.get(trait, set())) / 3))
            importance = TRAIT_IMPORTANCE.get(trait, 0.6)
            trait_needs.append(uncertainty * 0.35 + contradiction * 0.25 + importance * 0.25 + context_gap * 0.15)
        unresolved_need = sum(trait_needs) / len(trait_needs) if trait_needs else 0.35
        type_frequency = state.type_counts.get(question["question_type"], 0)
        type_diversity = 1 / (1 + 0.18 * type_frequency)
        family_count = sum(1 for entry in state.evidence if entry.get("evidence_family") == question["evidence_family"])
        novelty = 1 / (1 + 0.65 * family_count)
        resolver_traits = set(question.get("contradiction_resolver_for", []))
        resolver_bonus = 1.5 if resolver_traits and any(state.contradiction_scores.get(trait, 0) >= 0.15 for trait in resolver_traits) else 1.0
        fatigue_penalty = 1.0 - min(0.35, state.fatigue_score * 0.35)
        return question["diagnostic_value"] * unresolved_need * coverage_need * type_diversity * novelty * resolver_bonus * fatigue_penalty
