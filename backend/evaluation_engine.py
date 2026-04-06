import logging
from typing import List, Dict, Any

logger = logging.getLogger("mirofish.evaluation")

# ---------------------------------------------------------------------------
# Primary score: response-category distribution
#
# The simulation already made a "judgment call" by choosing a response
# category (compromise, escalate, assert, etc.) based on the agents'
# trait profiles and tension level.  That category is the most direct
# signal of relationship health — far more reliable than keyword matching
# over templated text.
#
# Score is built by summing per-message category weights, normalising to
# 0-100, then adjusting with keyword bonuses/penalties as secondary signal.
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS: Dict[str, int] = {
    "repair":      +15,   # proactive de-escalation
    "compromise":  +10,   # constructive engagement
    "defer":       -3,    # short-term peace, long-term resentment risk
    "assert":      -6,    # directness that risks escalation
    "withdraw":    -10,   # avoidance compounds over time
    "strained":    -12,   # visible resentment leaking into interaction
    "escalate":    -22,   # contempt/hostility; most predictive of breakdown
}

# Normalisation anchors — define the practical extremes for 8 messages (4 turns)
# so the category score maps sensibly to 0-100.
_CAT_WORST = 8 * CATEGORY_WEIGHTS["escalate"]   # = -176  (all escalate)
_CAT_BEST  = 8 * CATEGORY_WEIGHTS["repair"]     # = +120  (all repair)
_CAT_RANGE = _CAT_BEST - _CAT_WORST             # =  296

# Keyword adjustment weights (secondary; scaled down so keywords don't
# overwhelm the behavioural signal but can tip close calls).
HORSEMEN_WEIGHTS = {
    "criticism":    4,
    "contempt":     8,
    "defensiveness":3,
    "stonewalling": 5,
}

INDIAN_CONTEXT_STRESSORS = {
    "appeasement":  3,
    "non_defense":  8,
    "guilt_tripping":6,
    "exclusion":    5,
}


class EvaluationEngine:
    def __init__(self, history: List[Dict[str, str]]):
        self.history = history
        self.analysis = {
            "harmony_score": 50,
            "horsemen": {
                "criticism": 0, "contempt": 0,
                "defensiveness": 0, "stonewalling": 0,
            },
            "cultural_stressors": {
                "appeasement": 0, "non_defense": 0,
                "guilt_tripping": 0, "exclusion": 0,
            },
            "repair_attempts": 0,
            "synergies": [],
            "trajectory": "stable",
        }

    def compute(self) -> Dict[str, Any]:
        self._score_from_categories()
        self._analyze_keywords()
        self._detect_synergies()
        self._finalize_score()
        self._log_evaluation()
        return {
            "harmony_score": self.analysis["harmony_score"],
            "horsemen": self.analysis["horsemen"],
            "cultural_stressors": self.analysis["cultural_stressors"],
            "synergies": self.analysis["synergies"],
            "trajectory": self.analysis["trajectory"],
            "inference": self.analysis["inference"],
            "dialogue_history": self.history,
        }

    def _score_from_categories(self):
        """Primary scoring: sum category weights from _category tags."""
        raw = 0
        n = 0
        for turn in self.history:
            if turn["speaker"] == "Scene Master":
                continue
            cat = turn.get("_category", "")
            if cat in CATEGORY_WEIGHTS:
                raw += CATEGORY_WEIGHTS[cat]
                n += 1

        if n == 0:
            # No tagged turns — fall back to neutral
            self._cat_raw = 0
            self._n_messages = 0
        else:
            self._cat_raw = raw
            self._n_messages = n

        # Normalise raw to 0-100 using anchors scaled for actual message count
        if n > 0:
            worst = n * CATEGORY_WEIGHTS["escalate"]
            best  = n * CATEGORY_WEIGHTS["repair"]
            span  = best - worst
            self._cat_score_0_100 = (raw - worst) / span * 100 if span else 50
        else:
            self._cat_score_0_100 = 50.0

    def _analyze_keywords(self):
        """Secondary: keyword detection in dialogue text."""
        for turn in self.history:
            if turn["speaker"] == "Scene Master":
                continue

            msg = turn["message"].lower()
            detections = []

            if any(w in msg for w in [
                "always", "never", "every time", "you always", "you never",
            ]):
                self.analysis["horsemen"]["criticism"] += 1
                detections.append("criticism")

            if any(w in msg for w in [
                "disgusting", "disgust", "eye roll", "pathetic", "sick of",
                "contempt",
            ]):
                self.analysis["horsemen"]["contempt"] += 1
                detections.append("contempt")

            if any(w in msg for w in [
                "not my fault", "isn't my fault", "but you", "you're the one",
                "it's not like", "i didn't",
            ]):
                self.analysis["horsemen"]["defensiveness"] += 1
                detections.append("defensiveness")

            if any(w in msg for w in [
                "nothing more to say", "whatever you want", "just drop it",
                "can't do this", "made up your mind",
            ]):
                self.analysis["horsemen"]["stonewalling"] += 1
                detections.append("stonewalling")
            stripped = msg.strip()
            if stripped.endswith("...") and len(stripped) < 20:
                self.analysis["horsemen"]["stonewalling"] += 1
                detections.append("stonewalling(silence)")

            if "elders" in msg and any(w in msg for w in [
                "must", "should", "have to", "duty", "expect",
            ]):
                self.analysis["cultural_stressors"]["appeasement"] += 1
                detections.append("cultural:appeasement")

            if any(w in msg for w in [
                "don't react", "don't say anything", "stay silent",
                "keep quiet", "don't make a scene",
            ]):
                self.analysis["cultural_stressors"]["non_defense"] += 1
                detections.append("cultural:non_defense")

            if any(w in msg for w in [
                "after everything", "sacrificed so much", "they raised",
                "they gave up", "ungrateful",
            ]):
                self.analysis["cultural_stressors"]["guilt_tripping"] += 1
                detections.append("cultural:guilt_tripping")

            if any(w in msg for w in [
                "this isn't your concern", "stay out of", "not your place",
                "not your business",
            ]):
                self.analysis["cultural_stressors"]["exclusion"] += 1
                detections.append("cultural:exclusion")

            repair_phrases = [
                "i'm sorry", "hear you", "i understand", "let's try",
                "work through", "together", "compromise", "we're a team",
                "find a compromise", "meet me halfway", "find a solution",
                "brainstorm", "work as a team",
            ]
            repair_hits = sum(1 for p in repair_phrases if p in msg)
            if repair_hits >= 2:
                self.analysis["repair_attempts"] += 1
                detections.append(f"repair({repair_hits} phrases)")

            if detections:
                category = turn.get("_category", "?")
                logger.info(
                    "  Msg [%s|%s] detected: %s",
                    turn["speaker"], category, ", ".join(detections),
                )

    def _detect_synergies(self):
        a_msgs = [
            t["message"].lower() for t in self.history if t["speaker"] == "Agent A"
        ]
        b_msgs = [
            t["message"].lower() for t in self.history if t["speaker"] == "Agent B"
        ]
        a_text = " ".join(a_msgs)
        b_text = " ".join(b_msgs)

        if "fairness" in a_text and "fairness" in b_text:
            self.analysis["synergies"].append("Shared Value: High Fairness Orientation")

        if ("team" in a_text or "together" in a_text) and \
           ("team" in b_text or "together" in b_text):
            self.analysis["synergies"].append("Collaborative Mindset: Partnership Orientation")

        if self.analysis["repair_attempts"] >= 5:
            self.analysis["synergies"].append("Repair Skill: Strong mutual de-escalation capacity")
        elif self.analysis["repair_attempts"] >= 3:
            self.analysis["synergies"].append("Repair Potential: Willingness to de-escalate")

    def _finalize_score(self):
        # Primary: category-derived score (0-100)
        cat_score = self._cat_score_0_100

        # Secondary keyword adjustments (±points)
        horse_penalty = sum(
            self.analysis["horsemen"][h] * HORSEMEN_WEIGHTS[h]
            for h in HORSEMEN_WEIGHTS
        )
        cult_penalty = sum(
            self.analysis["cultural_stressors"][s] * INDIAN_CONTEXT_STRESSORS[s]
            for s in INDIAN_CONTEXT_STRESSORS
        )
        repair_bonus  = self.analysis["repair_attempts"] * 3
        synergy_bonus = len(self.analysis["synergies"]) * 4

        final = cat_score - horse_penalty - cult_penalty + repair_bonus + synergy_bonus
        self.analysis["harmony_score"] = max(0, min(100, int(final)))

        # Trajectory based on category raw signal
        n = self._n_messages or 1
        # Per-message average category contribution
        per_msg = self._cat_raw / n

        if per_msg <= CATEGORY_WEIGHTS["escalate"] * 0.6:      # dominated by escalation
            self.analysis["trajectory"] = "downward-spiral"
        elif per_msg < 0:
            if horse_penalty > 15 and repair_bonus < 6:
                self.analysis["trajectory"] = "at-risk"
            else:
                self.analysis["trajectory"] = "unstable"
        elif per_msg >= CATEGORY_WEIGHTS["repair"] * 0.6:
            self.analysis["trajectory"] = "harmonious"
        elif per_msg >= CATEGORY_WEIGHTS["compromise"] * 0.6 and horse_penalty < 8:
            self.analysis["trajectory"] = "recovery"
        else:
            self.analysis["trajectory"] = "stable"

        self._score_breakdown = {
            "cat_score": round(cat_score, 1),
            "horsemen_penalty": horse_penalty,
            "cultural_penalty": cult_penalty,
            "repair_bonus": repair_bonus,
            "synergy_bonus": synergy_bonus,
        }

        self.analysis["inference"] = self._build_inference(
            cat_score, horse_penalty, cult_penalty, repair_bonus, synergy_bonus,
        )

    def _build_inference(
        self, cat_score: float, horse_penalty: int, cult_penalty: int,
        repair_bonus: int, synergy_bonus: int,
    ) -> str:
        score = self.analysis["harmony_score"]
        trajectory = self.analysis["trajectory"]
        parts = []

        # Primary driver
        n = self._n_messages or 1
        per_msg = self._cat_raw / n
        if per_msg >= 8:
            parts.append("consistent constructive engagement (+behaviour)")
        elif per_msg >= 0:
            parts.append("mixed behaviour pattern")
        elif per_msg >= -8:
            parts.append("tension-driven exchanges dominate")
        else:
            parts.append("hostile/escalating exchanges dominate")

        # Horsemen
        top_h = max(self.analysis["horsemen"], key=self.analysis["horsemen"].get)
        top_h_n = self.analysis["horsemen"][top_h]
        if horse_penalty > 0:
            parts.append(f"{top_h} detected ({top_h_n}x, -{horse_penalty}pts)")

        # Cultural stressors
        top_c = max(self.analysis["cultural_stressors"], key=self.analysis["cultural_stressors"].get)
        top_c_n = self.analysis["cultural_stressors"][top_c]
        if cult_penalty > 0:
            parts.append(f"cultural stressor '{top_c}' ({top_c_n}x, -{cult_penalty}pts)")

        # Repair / synergy
        if repair_bonus > 0:
            parts.append(f"{self.analysis['repair_attempts']} repair attempts (+{repair_bonus}pts)")
        if synergy_bonus > 0:
            parts.append(f"{len(self.analysis['synergies'])} synergies (+{synergy_bonus}pts)")

        return f"Score {score}/100 [{trajectory.upper()}]: " + "; ".join(parts) + "."

    def _log_evaluation(self):
        b = self._score_breakdown
        logger.info("  EVALUATION SCORE BREAKDOWN:")
        logger.info(
            "    cat_score=%.1f - horsemen=%d - cultural=%d + repair=%d + synergy=%d = %d",
            b["cat_score"], b["horsemen_penalty"], b["cultural_penalty"],
            b["repair_bonus"], b["synergy_bonus"],
            self.analysis["harmony_score"],
        )
        if self.analysis["synergies"]:
            logger.info("    Synergies: %s", " | ".join(self.analysis["synergies"]))
        logger.info("  INFERENCE: %s", self.analysis["inference"])
        logger.info("=" * 70)


def compute_harmony_index(history: List[Dict[str, str]]) -> Dict[str, Any]:
    engine = EvaluationEngine(history)
    return engine.compute()
