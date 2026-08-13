"""Run a synthetic persona through the adaptive intake using a local Ollama model.

This is intentionally an offline test harness. It records every selected
question, raw model answer, and resulting deterministic evidence distribution
so adaptive routing can be evaluated without changing the production bank.
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from adaptive_router import AdaptiveIntakeState, AdaptiveQuestionRouter
from synthetic_testing.schemas.persona_spec import SyntheticPersonaSpec


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.environ.get("ADAPTIVE_TEST_MODEL", "qwen3:4b")
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"


class OllamaUnavailable(RuntimeError):
    pass


def _answer_prompt(persona: SyntheticPersonaSpec, question: Dict[str, Any]) -> str:
    options = question.get("options", [])
    if question.get("format") == "probe_group":
        options = question["probes"][0].get("options", [])
    fmt = question.get("format", "multiple_choice")
    if fmt in {"scale_6", "scale_7", "importance_scale"}:
        response_contract = 'Return exactly: {"answer": <integer from 1 to 7>}'
    elif fmt in {"short_answer", "text_input"}:
        response_contract = 'Return exactly: {"answer": "one or two concise sentences"}'
    elif fmt == "probe_group":
        response_contract = (
            'Return exactly: {"answer": {"action": "one exact allowed option", '
            '"emotion": "brief emotion", "reflection": "brief reflection"}}'
        )
    else:
        response_contract = 'Return exactly: {"answer": "one exact allowed option"}'
    return f"""You are roleplaying this synthetic testing persona:
{persona.ollama_behavioral_brief}

Answer the approved questionnaire item consistently with that persona. Do not
explain your reasoning. Return strict JSON only.

Question id: {question['id']}
Question: {question['text']}
Format: {fmt}
Allowed options: {json.dumps(options)}

{response_contract}
"""


def _generate(prompt: str, seed: int) -> Any:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"seed": seed, "temperature": 0.25},
    }
    try:
        request = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            response_body = json.loads(response.read().decode("utf-8"))
        return json.loads(response_body["response"])
    except urllib.error.URLError as exc:
        raise OllamaUnavailable(f"Ollama is unavailable at {OLLAMA_URL}: {exc.reason}") from exc
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama returned an invalid answer payload: {exc}") from exc


def _generate_valid_answer(persona: SyntheticPersonaSpec, question: Dict[str, Any], seed: int) -> Any:
    """Retry malformed structured output without substituting a fabricated answer."""
    prompt = _answer_prompt(persona, question)
    raw_answers = []
    for attempt in range(3):
        if attempt:
            prompt += "\nYour previous response did not match an approved option. Return only valid JSON using an exact allowed option."
        raw = _generate(prompt, seed + attempt)
        validated = _validate_answer(question, raw)
        if validated is not None:
            return validated
        raw_answers.append(raw)
    raise RuntimeError(f"Invalid {MODEL_NAME} answer for {question['id']} after 3 attempts: {raw_answers!r}")


def _validate_answer(question: Dict[str, Any], answer: Any) -> Optional[Any]:
    fmt = question.get("format")
    payload = answer if isinstance(answer, dict) else {"answer": answer}
    answer = payload.get("answer")
    if fmt in {"scale_6", "scale_7", "importance_scale"}:
        try:
            return max(1, min(7, int(answer)))
        except (TypeError, ValueError):
            return None
    if fmt in {"short_answer", "text_input"}:
        return answer if isinstance(answer, str) and answer.strip() else None
    if fmt == "probe_group":
        options = question["probes"][0].get("options", [])
        allowed = {item.get("id", item.get("text")) if isinstance(item, dict) else item for item in options}
        if not isinstance(answer, dict) and payload.get("id") in allowed:
            # Some small models flatten a micro-bundle into its primary action.
            # Keep that answer, but do not fabricate emotion or reflection.
            return {"action": payload["id"]}
        if not isinstance(answer, dict):
            return None
        if "action" not in answer and payload.get("id") in allowed:
            return {"action": payload["id"]}
        action = _match_allowed(answer.get("action"), allowed)
        if action is None:
            return None
        return {**answer, "action": action}
    allowed_ids = set()
    text_to_id = {}
    for item in question.get("options", []):
        if isinstance(item, dict):
            allowed_ids.add(item.get("id"))
            if "text" in item:
                text_to_id[item["text"].strip().casefold().replace("'", "’")] = item.get("id")
        else:
            allowed_ids.add(item)
            
    matched = _match_allowed(answer, allowed_ids)
    if matched is not None:
        return matched
        
    # Check if they output the text instead of the ID
    if isinstance(answer, str):
        normalized = answer.strip().casefold().replace("'", "’")
        if normalized in text_to_id:
            return text_to_id[normalized]

    # Small models sometimes emit both an option ID and a mistaken scalar
    # answer. Prefer the approved ID only when it validates exactly.
    fallback_id = payload.get("id")
    return _match_allowed(fallback_id, allowed_ids)

def _match_allowed(value: Any, allowed: set[Any]) -> Optional[Any]:
    if value in allowed:
        return value
    if not isinstance(value, str):
        return None
    normalized = value.strip().casefold().replace("'", "’")
    for candidate in allowed:
        if isinstance(candidate, str) and candidate.casefold().replace("'", "’") == normalized:
            return candidate
    return None


def run_adaptive_persona(persona_path: str, seed: int = 42) -> Dict[str, Any]:
    with open(persona_path, "r") as handle:
        persona = SyntheticPersonaSpec(**yaml.safe_load(handle))
    router = AdaptiveQuestionRouter(seed=seed)
    state = AdaptiveIntakeState()
    transcript = []

    while not router.should_stop(state):
        question = router.select_next(state)
        if question is None:
            break
        answer = _generate_valid_answer(persona, question, seed + state.question_count)
        router.update_state(state, question["id"], answer)
        transcript.append({"question_id": question["id"], "answer": answer})
        if os.environ.get("ADAPTIVE_TEST_VERBOSE") == "1" and state.question_count % 25 == 0:
            print(f"{persona.id}: answered {state.question_count} adaptive questions", flush=True)

    result = {
        "persona_id": persona.id,
        "persona_version": persona.version,
        "model": MODEL_NAME,
        "seed": seed,
        "transcript": transcript,
        "progress": router.get_progress(state),
        "trait_distributions": state.trait_distributions,
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORTS_DIR / f"adaptive_{persona.id}_{seed}.json"
    with open(output_path, "w") as handle:
        json.dump(result, handle, indent=2)
    return result
