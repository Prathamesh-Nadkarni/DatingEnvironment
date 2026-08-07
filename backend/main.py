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

app = FastAPI(title="MiroFish Agentic Matchmaking API")

# Simple In-Memory DB for Demo
db = {
    "user_prompts": {
        1: "You are the User (Agent A).",
        2: "You are the Match (Agent B).",
    },
    "user_answers": {}
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
    user_id: int
    answers: Dict[str, Any]

@app.get("/api/onboarding/questions")
def get_questions():
    return {"sections": get_intake_data()}

@app.post("/api/onboarding/submit")
def submit_onboarding(submission: SurveySubmission):
    # 1. Store raw answers
    db["user_answers"][submission.user_id] = submission.answers
    
    # 2. Synthesize Persona through 9-step pipeline
    persona_prompt = analyze_answers(submission.answers)
    
    # 3. Store the prompt for simulation
    db["user_prompts"][submission.user_id] = persona_prompt
    
    print(f"Persona Synthesized for User {submission.user_id}")
    return {"status": "success", "message": "Persona synthesized."}

@app.get("/api/scenarios")
def get_scens():
    return {"scenarios": scenarios.get_scenarios()}

class SimulationRequest(BaseModel):
    user_a_id: int
    user_b_id: int
    scenario_id: Optional[str] = None
    max_turns: int = 5

@app.post("/api/simulation/run")
def start_simulation(req: SimulationRequest):
    # 1. Resolve scenario
    all_scenarios = {s["id"]: s for s in scenarios.get_scenarios()}
    scenario_data = all_scenarios.get(req.scenario_id or "unannounced_guests")
    
    # 2. Retrieve Prompts
    prompt_a = db["user_prompts"].get(req.user_a_id, "You are a standard persona.")
    prompt_b = db["user_prompts"].get(req.user_b_id, "You are a traditional match.")
    
    # 3. Execute LangGraph Simulation
    result = run_simulation(prompt_a, prompt_b, scenario_data, max_turns=req.max_turns)
    
    # 4. Behavioral Analytics & Harmony Index
    analysis = compute_harmony_index(result["dialogue_history"])
    
    return {
        "status": "success", 
        "harmony_score": analysis["harmony_score"],
        "horsemen": analysis["horsemen"],
        "cultural_stressors": analysis["cultural_stressors"],
        "synergies": analysis["synergies"],
        "trajectory": analysis["trajectory"],
        "inference": analysis.get("inference", ""),
        "dialogue_history": result["dialogue_history"]
    }

class CompatibilityRequest(BaseModel):
    user_a_id: int
    user_b_id: int
    max_turns: int = 4

@app.post("/api/compatibility/report")
def get_compatibility_report(req: CompatibilityRequest):
    prompt_a = db["user_prompts"].get(req.user_a_id, "You are a standard persona.")
    prompt_b = db["user_prompts"].get(req.user_b_id, "You are a traditional match.")

    report = run_full_compatibility_report(prompt_a, prompt_b, max_turns=req.max_turns)

    return {
        "status": "success",
        "user_a_id": req.user_a_id,
        "user_b_id": req.user_b_id,
        **report,
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
