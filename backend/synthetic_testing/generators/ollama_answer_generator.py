import json
import hashlib
import os
import urllib.request
import logging
from typing import Dict, Any
from synthetic_testing.schemas.persona_spec import SyntheticPersonaSpec
from synthetic_testing.prompts.answer_generator import get_synthetic_answer_prompt
from synthetic_testing.config import ANSWERS_CACHE_DIR

logger = logging.getLogger(__name__)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

class SyntheticAnswerGenerator:
    def __init__(self, questionnaire_version: str = "v1", prompt_version: str = "v1"):
        self.questionnaire_version = questionnaire_version
        self.prompt_version = prompt_version

    def _get_cache_path(self, persona: SyntheticPersonaSpec, seed: int) -> str:
        key_str = f"{persona.version}_{self.questionnaire_version}_{MODEL_NAME}_{self.prompt_version}_{seed}"
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        persona_dir = os.path.join(ANSWERS_CACHE_DIR, persona.id)
        os.makedirs(persona_dir, exist_ok=True)
        return os.path.join(persona_dir, f"{key_hash}.json")

    def generate(self, persona: SyntheticPersonaSpec, questionnaire: Dict[str, Any], seed: int, use_cache: bool = True) -> Dict[str, Any]:
        cache_path = self._get_cache_path(persona, seed)
        if use_cache and os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)

        answers = {}
        for section, questions in questionnaire.items():
            for q_id, q_data in questions.items():
                prompt = get_synthetic_answer_prompt(persona.ollama_behavioral_brief, q_data.get("text", str(q_data)))
                payload = {
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"seed": seed}
                }
                try:
                    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode('utf-8'),
                                                 headers={'Content-Type': 'application/json'})
                    response = urllib.request.urlopen(req, timeout=10)
                    result = json.loads(response.read().decode('utf-8'))
                    answers[q_id] = result.get('response', '...').strip(' \\n"')
                except Exception as e:
                    logger.error(f"Error generating answer for {q_id}: {e}")
                    answers[q_id] = "[Generation failed]"

        result_set = {
            "persona_id": persona.id,
            "persona_version": persona.version,
            "questionnaire_version": self.questionnaire_version,
            "ollama_model": MODEL_NAME,
            "seed": seed,
            "answers": answers,
            "generation_metadata": {}
        }

        with open(cache_path, "w") as f:
            json.dump(result_set, f, indent=2)

        return result_set
