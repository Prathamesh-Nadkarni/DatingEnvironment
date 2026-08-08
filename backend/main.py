import logging
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s | %(message)s",
)

import scenarios
from intake_questions import get_intake_data
from persona_synthesis import analyze_answers
from simulation_engine import run_simulation
from evaluation_engine import compute_harmony_index
from compatibility_engine import run_full_compatibility_report
from astrology import get_astro_fingerprint, get_astakoota_score

app = FastAPI(title="MiroFish Agentic Matchmaking API")

# Simple In-Memory DB for Demo
db = {
    "sessions": {
        # "session_id": { "user_a": {"prompt": "...", "answers": {}}, "user_b": {"prompt": "...", "answers": {}} }
    }
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

class SurveySubmission(BaseModel):
    session_id: str
    role: str # "user_a" or "user_b"
    answers: Dict[str, Any]
    demographics: Dict[str, str] = {}

@app.get("/api/onboarding/questions")
def get_questions():
    return {"sections": get_intake_data()}

@app.post("/api/onboarding/submit")
def submit_onboarding(submission: SurveySubmission):
    session_id = submission.session_id
    role = submission.role

    if session_id not in db["sessions"]:
        db["sessions"][session_id] = {}
        
    if role not in db["sessions"][session_id]:
        db["sessions"][session_id][role] = {}

    # 1. Store raw answers
    db["sessions"][session_id][role]["answers"] = submission.answers
    
    # 2. Extract demographics and compute Astro Fingerprint
    if submission.demographics:
        fingerprint = get_astro_fingerprint(
            submission.demographics.get("fullName", ""),
            submission.demographics.get("birthDate", ""),
            submission.demographics.get("birthTime", ""),
            submission.demographics.get("birthCity", "")
        )
        db["sessions"][session_id][role]["astro_fingerprint"] = fingerprint
    
    # 3. Synthesize Persona through 9-step pipeline
    persona_prompt = analyze_answers(submission.answers)
    
    # 4. Store the prompt for simulation
    db["sessions"][session_id][role]["prompt"] = persona_prompt
    
    print(f"Persona Synthesized for Session {session_id} Role {role}")
    return {"status": "success", "message": "Persona synthesized."}

@app.get("/api/session/status/{session_id}")
def check_session_status(session_id: str):
    if session_id not in db["sessions"]:
        return {"ready": False}
    
    session = db["sessions"][session_id]
    user_a_ready = "user_a" in session and "prompt" in session["user_a"]
    user_b_ready = "user_b" in session and "prompt" in session["user_b"]
    
    return {
        "ready": user_a_ready and user_b_ready,
        "user_a_ready": user_a_ready,
        "user_b_ready": user_b_ready
    }

@app.get("/api/scenarios")
def get_scens():
    return {"scenarios": scenarios.get_scenarios()}

class SimulationRequest(BaseModel):
    session_id: str
    scenario_id: Optional[str] = None
    max_turns: int = 5

@app.post("/api/simulation/run")
def start_simulation(req: SimulationRequest):
    # 1. Resolve scenario
    all_scenarios = {s["id"]: s for s in scenarios.get_scenarios()}
    scenario_data = all_scenarios.get(req.scenario_id or "unannounced_guests")
    
    # 2. Retrieve Prompts
    session = db["sessions"].get(req.session_id, {})
    prompt_a = session.get("user_a", {}).get("prompt", "You are a standard persona.")
    prompt_b = session.get("user_b", {}).get("prompt", "You are a traditional match.")
    
    # 3. Execute LangGraph Simulation
    result = run_simulation(prompt_a, prompt_b, scenario_data, max_turns=req.max_turns)
    
    # 4. Behavioral Analytics & Harmony Index
    analysis = compute_harmony_index(result["dialogue_history"])
    
    # Compute Kundali score if both have astrological fingerprints
    kundali_data = None
    user_a = session.get("user_a", {})
    user_b = session.get("user_b", {})
    if "astro_fingerprint" in user_a and "astro_fingerprint" in user_b:
        kundali_data = get_astakoota_score(
            user_a["astro_fingerprint"]["moon_class"],
            user_b["astro_fingerprint"]["moon_class"]
        )
    
    return {
        "status": "success", 
        "harmony_score": analysis["harmony_score"],
        "horsemen": analysis["horsemen"],
        "cultural_stressors": analysis["cultural_stressors"],
        "synergies": analysis["synergies"],
        "trajectory": analysis["trajectory"],
        "inference": analysis.get("inference", ""),
        "dialogue_history": result["dialogue_history"],
        "kundali": kundali_data
    }

class CompatibilityRequest(BaseModel):
    session_id: str
    max_turns: int = 4

@app.post("/api/compatibility/report")
def get_compatibility_report(req: CompatibilityRequest):
    session = db["sessions"].get(req.session_id, {})
    
    user_a = session.get("user_a", {})
    user_b = session.get("user_b", {})
    
    prompt_a = user_a.get("prompt", "You are a standard persona.")
    prompt_b = user_b.get("prompt", "You are a traditional match.")

    report = run_full_compatibility_report(prompt_a, prompt_b, max_turns=req.max_turns)
    
    # Compute Kundali score if both have astrological fingerprints
    kundali_data = None
    if "astro_fingerprint" in user_a and "astro_fingerprint" in user_b:
        kundali_data = get_astakoota_score(
            user_a["astro_fingerprint"]["moon_class"],
            user_b["astro_fingerprint"]["moon_class"]
        )

    return {
        "status": "success",
        "session_id": req.session_id,
        "kundali": kundali_data,
        **report,
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
