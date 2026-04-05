from typing import List, Dict, Any

# MiroFish Evaluation Logic: Harmony Index and Behavioral Analytics
HORSEMEN_WEIGHTS = {
    "criticism": 8,
    "contempt": 15,    # Nuclear bomb for relationships
    "defensiveness": 6,
    "stonewalling": 10
}

INDIAN_CONTEXT_STRESSORS = {
    "appeasement": 5,        # Leading to future resentment
    "non_defense": 12,       # Public betrayal of spouse
    "guilt_tripping": 10,    # Using family obligation as a weapon
    "exclusion": 7           # Excluding spouse/family from decision
}

class EvaluationEngine:
    def __init__(self, history: List[Dict[str, str]]):
        self.history = history
        self.analysis = {
            "harmony_score": 75, # Baseline
            "horsemen": {"criticism": 0, "contempt": 0, "defensiveness": 0, "stonewalling": 0},
            "cultural_stressors": {"appeasement": 0, "non_defense": 0, "guilt_tripping": 0, "exclusion": 0},
            "repair_attempts": 0,
            "synergies": [],
            "trajectory": "stable"
        }

    def compute(self) -> Dict[str, Any]:
        """Calculates final Harmony Index and detailed transcript analysis."""
        self._analyze_sentiment_and_patterns()
        self._detect_synergies()
        self._finalize_score()
        
        return {
            "harmony_score": self.analysis["harmony_score"],
            "horsemen": self.analysis["horsemen"],
            "cultural_stressors": self.analysis["cultural_stressors"],
            "synergies": self.analysis["synergies"],
            "trajectory": self.analysis["trajectory"],
            "dialogue_history": self.history
        }

    def _analyze_sentiment_and_patterns(self):
        sentiment_path = []
        for turn in self.history:
            msg = turn["message"].lower()
            thought = ""
            if "<InternalThought>" in turn["message"]:
                thought = turn["message"].split("<InternalThought>")[1].split("</InternalThought>")[0].lower()
            
            # Pattern Detection
            if "always" in msg or "never" in msg: self.analysis["horsemen"]["criticism"] += 1
            if "eye roll" in msg or "disgust" in msg: self.analysis["horsemen"]["contempt"] += 1
            if "not my fault" in msg or "but you" in msg: self.analysis["horsemen"]["defensiveness"] += 1
            if "..." in msg or "fine." == msg: self.analysis["horsemen"]["stonewalling"] += 1

            # Indian Context Patterns
            if " elders " in msg and "must" in msg: self.analysis["cultural_stressors"]["appeasement"] += 1
            if "don't react" in msg or "don't say anything" in msg: self.analysis["cultural_stressors"]["non_defense"] += 1
            if "after everything parents did" in msg: self.analysis["cultural_stressors"]["guilt_tripping"] += 1
            
            # Repair Attempts
            if "sorry" in msg or "hear you" in msg or "understand" in msg:
                self.analysis["repair_attempts"] += 1

    def _detect_synergies(self):
        # Placeholder for complex value matching logic
        # If both agents mention 'fairness' in thought, it's a synergy
        thoughts = [t["message"] for t in self.history if "<InternalThought>" in t["message"]]
        if any("fairness" in t.lower() for t in thoughts) and len(thoughts) > 1:
            self.analysis["synergies"].append("Shared Value: High Egalitarianism/Fairness Orientation")
        
        if self.analysis["repair_attempts"] > 2:
            self.analysis["synergies"].append("Repair Skill: Mutual willingness to de-escalate")

    def _finalize_score(self):
        # Calculate Penalties
        horse_penalty = sum(self.analysis["horsemen"][h] * HORSEMEN_WEIGHTS[h] for h in HORSEMEN_WEIGHTS)
        cult_penalty = sum(self.analysis["cultural_stressors"][s] * INDIAN_CONTEXT_STRESSORS[s] for s in INDIAN_CONTEXT_STRESSORS)
        
        # Calculate Rewards
        repair_bonus = self.analysis["repair_attempts"] * 5
        
        final = 70 - horse_penalty - cult_penalty + repair_bonus
        self.analysis["harmony_score"] = max(0, min(100, int(final)))
        
        if horse_penalty > 30: self.analysis["trajectory"] = "downward-spiral"
        elif repair_bonus > 15: self.analysis["trajectory"] = "recovery"
        else: self.analysis["trajectory"] = "stable"

def compute_harmony_index(history: List[Dict[str, str]]) -> Dict[str, Any]:
    engine = EvaluationEngine(history)
    return engine.compute()
