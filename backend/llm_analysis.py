import json
import urllib.request
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

def analyze_text_compatibility(answers_a: Dict[str, str], answers_b: Dict[str, str]) -> Tuple[int, str]:
    """
    Takes dictionaries of {question_text: user_answer} for both users.
    Calls Llama 3.2 via Ollama to evaluate stylistic, tonal, and semantic compatibility.
    Returns (score_0_to_100, reasoning_string).
    """
    if not answers_a or not answers_b:
        return 50, "Not enough text data to analyze."

    prompt = f"""
You are an expert relationship psychologist and linguistic analyst.
I will provide you with the open-ended text answers from two individuals (User A and User B) to the same relationship intake questions.

Your task is to analyze their answers and determine their compatibility based on two major factors:
1. Semantic Alignment: Do they want the same things? Do their values and boundaries align?
2. Stylistic & Tonal Compatibility: Analyze their tone, language, grammar, and writing style. Are they both formal? Both casual? Does one sound highly articulate while the other sounds terse or careless? Mismatched communication styles often lead to friction.

User A Answers:
{json.dumps(answers_a, indent=2)}

User B Answers:
{json.dumps(answers_b, indent=2)}

Output your analysis as a strict JSON object with exactly two keys:
- "score": an integer from 0 to 100 representing their text/style compatibility.
- "reasoning": a brief 2-sentence explanation of why they received this score, explicitly mentioning their tone/style alignment.

JSON Output:
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        
        response_text = result.get('response', '{}')
        parsed = json.loads(response_text)
        
        score = parsed.get("score", 50)
        reasoning = parsed.get("reasoning", "Analysis complete.")
        
        # Ensure score is within bounds
        score = max(0, min(100, int(score)))
        
        return score, reasoning
        
    except Exception as e:
        logger.error(f"Error calling Ollama for text analysis: {e}")
        return 50, "LLM analysis failed or timed out."


def generate_agent_dialogue(scenario_desc: str, action: str, history: List[Dict], user_tone_answers: Dict[str, str], agent_name: str) -> str:
    """
    Generates dialogue for a simulation turn using Llama 3.2, 
    matching the user's specific text-response tone.
    """
    if not user_tone_answers:
        tone_sample = "Casual and standard."
    else:
        tone_sample = json.dumps(user_tone_answers, indent=2)
        
    history_str = "\n".join([f"{msg['speaker']}: {msg.get('message', '')}" for msg in history])
    
    prompt = f"""
You are roleplaying as {agent_name} in a relationship simulation.
Scenario: {scenario_desc}

Your exact tone, language style, and maturity level should mimic these sample answers provided by the user:
{tone_sample}

Conversation so far:
{history_str}

Your system has determined you must execute this action: {action.upper()}
(For example: COMPROMISE means de-escalating and yielding, ASSERT means standing firm, WITHDRAW means going cold or silent, ESCALATE means becoming toxic/critical, REPAIR means attempting to fix the bond).

Write EXACTLY what {agent_name} says next. Do not include quotes, actions, or descriptions. Just the raw dialogue text. Keep it under 2 sentences.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }

    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        return result.get('response', '...').strip(' \n"')
    except Exception as e:
        logger.error(f"Error generating dialogue: {e}")
        # Fallback to hardcoded if LLM fails
        return f"[Failed to generate: {action}]"


def evaluate_simulation_transcript(scenario_desc: str, transcript: List[Dict]) -> Dict:
    """
    Evaluates the full dialogue transcript for behavioral patterns using structured semantic detection.
    """
    history_str = "\n".join([f"{msg['speaker']} ({msg.get('action', msg.get('_category', ''))}): {msg.get('message', '')}" for msg in transcript])
    
    prompt = f"""
You are a Semantic Behavioral Evaluator for a relationship simulation.
Scenario: {scenario_desc}

Transcript:
{history_str}

Analyze the dialogue for underlying semantic behaviors. Do not just look for keywords; analyze the meaning and intent.
Output a JSON object with:
- "toxic_behaviors": A list of objects, each containing "behavior" (e.g., contempt, criticism, defensiveness, stonewalling), "confidence" (0.0 to 1.0), and "evidence" (a short quote).
- "repair_attempts": A list of objects containing "type" (e.g., de-escalation, validation, compromise), "confidence", and "evidence".
- "synergy_score": overall interaction health score (0-100).
- "reasoning": 2-sentence summary of the interaction dynamics.

JSON Output:
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=20)
        result = json.loads(response.read().decode('utf-8'))
        parsed = json.loads(result.get('response', '{}'))
        
        # Aggregate legacy counts for backwards compatibility if needed elsewhere
        horsemen = len(parsed.get("toxic_behaviors", []))
        repair = len(parsed.get("repair_attempts", []))
        
        return {
            "toxic_behaviors": parsed.get("toxic_behaviors", []),
            "repair_attempts": parsed.get("repair_attempts", []),
            "horsemen": horsemen,
            "repair": repair,
            "score": parsed.get("synergy_score", 50),
            "reasoning": parsed.get("reasoning", "No clear reasoning provided.")
        }
    except Exception as e:
        logger.error(f"Error evaluating transcript: {e}")
        return {"toxic_behaviors": [], "repair_attempts": [], "horsemen": 0, "repair": 0, "score": 50, "reasoning": "LLM evaluation failed."}


def analyze_behavioral_evidence_primary(question: str, answer: str, previous_evidence: List[Dict]) -> Dict:
    """
    Primary Analyst using qwen3:8b.
    Extracts structured behavioral evidence from free text or complex ambiguous answers.
    """
    prompt = f"""
You are a behavioral analyst. Your job is to extract relationship traits from a user's answer.
Question: {question}
User Answer: {answer}
Relevant Previous Evidence: {json.dumps(previous_evidence)}

Extract the following in strict JSON:
{{
  "perception": [],
  "emotions": [],
  "motivations": [],
  "behavioral_impulse": null,
  "likely_action": null,
  "trait_evidence": [{{"trait": "trait_name", "value": 0.0-1.0}}],
  "needs_evidence": [],
  "context_modifiers": [],
  "contradictions": [],
  "confidence": 0.0
}}
"""
    payload = {
        "model": "qwen3:8b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        parsed = json.loads(result.get('response', '{}'))
        return parsed
    except Exception as e:
        logger.error(f"Error calling Qwen3 for behavioral analysis: {e}")
        return {"trait_evidence": [], "confidence": 0.0}

def verify_behavioral_evidence(question: str, answer: str, previous_evidence: List[Dict]) -> Dict:
    """
    Independent Verifier using gemma3:4b.
    Focuses on alternative interpretations and evidence sufficiency.
    """
    prompt = f"""
You are an independent verifier. Your job is to analyze this answer and provide alternative interpretations.
Question: {question}
User Answer: {answer}
Relevant Previous Evidence: {json.dumps(previous_evidence)}

Provide your independent analysis in strict JSON:
{{
  "explicitly_supported": [],
  "ambiguous_elements": [],
  "alternative_explanations": [],
  "unjustified_traits": [],
  "trait_evidence": [{{"trait": "trait_name", "value": 0.0-1.0}}],
  "confidence": 0.0
}}
"""
    payload = {
        "model": "gemma3:4b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode('utf-8'))
        parsed = json.loads(result.get('response', '{}'))
        return parsed
    except Exception as e:
        logger.error(f"Error calling Gemma3 for verification: {e}")
        return {"trait_evidence": [], "confidence": 0.0}

if __name__ == "__main__":
    # Test script
    a = {"What does a genuine apology sound like to you?": "A genuine apology requires taking full accountability without making excuses, validating my feelings, and explaining how the behavior will change moving forward."}
    b = {"What does a genuine apology sound like to you?": "idk just say ur sorry and mean it"}
    
    score, reason = analyze_text_compatibility(a, b)
    print(f"Score: {score}/100")
    print(f"Reasoning: {reason}")

