import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Response, status
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware

# Set up standard logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up observability logger
obs_logger = logging.getLogger("observability")
obs_logger.setLevel(logging.INFO)
obs_handler = logging.FileHandler("observability.log")
obs_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
obs_logger.addHandler(obs_handler)
obs_logger.propagate = False

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

class TelemetryEvent(BaseModel):
    session_id: Optional[str] = None
    role: Optional[str] = None
    event_type: str
    element_id: Optional[str] = None
    time_taken_ms: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

@app.post("/api/telemetry")
def record_telemetry(event: TelemetryEvent):
    log_msg = f"Session: {event.session_id or 'anonymous'} | Role: {event.role or 'N/A'} | Event: {event.event_type}"
    if event.element_id:
        log_msg += f" | Element: {event.element_id}"
    if event.time_taken_ms is not None:
        log_msg += f" | Time(ms): {event.time_taken_ms}"
    if event.details:
        log_msg += f" | Details: {event.details}"
    
    obs_logger.info(log_msg)
    return {"status": "recorded"}

import os
import re

@app.get("/api/admin/sessions")
def get_admin_sessions():
    return {"sessions": db["sessions"]}

@app.get("/api/admin/telemetry")
def get_admin_telemetry():
    if not os.path.exists("observability.log"):
        return {"events": []}
    
    events = []
    # Regex to match: [timestamp] [level] Session: ... | Role: ... | Event: ... | Element: ... | Time(ms): ... | Details: ...
    # We can also just do simple string splitting since it's highly structured.
    with open("observability.log", "r") as f:
        for line in f:
            if not line.strip(): continue
            try:
                # [2026-08-09 01:45:21,244] [INFO] Session: local_demo | Role: user_a | Event: button_click ...
                parts = line.split("] [INFO] ")
                if len(parts) != 2: continue
                timestamp = parts[0].strip("[")
                data_part = parts[1].strip()
                
                event_obj = {"timestamp": timestamp}
                for pair in data_part.split(" | "):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        event_obj[k.strip().lower().replace("(ms)", "_ms")] = v.strip()
                events.append(event_obj)
            except Exception as e:
                continue
                
    return {"events": events}

class SurveySubmission(BaseModel):
    session_id: str
    role: str # "user_a" or "user_b"
    answers: Dict[str, Any]
    demographics: Dict[str, str] = {}

@app.get("/api/onboarding/questions")
def get_questions():
    return {"sections": get_intake_data()}

def generate_and_cache_report(session_id: str):
    session = db["sessions"].get(session_id, {})
    user_a = session.get("user_a", {})
    user_b = session.get("user_b", {})
    
    prompt_a = user_a.get("prompt", "You are a standard persona.")
    prompt_b = user_b.get("prompt", "You are a traditional match.")
    
    try:
        report = run_full_compatibility_report(
            prompt_a, 
            prompt_b, 
            answers_a=user_a.get("answers", {}), 
            answers_b=user_b.get("answers", {}),
            max_turns=4
        )
        
        kundali_data = None
        if "astro_fingerprint" in user_a and "astro_fingerprint" in user_b:
            kundali_data = get_astakoota_score(
                user_a["astro_fingerprint"]["moon_class"],
                user_b["astro_fingerprint"]["moon_class"]
            )
        
        session["cached_report"] = {
            "status": "success",
            "session_id": session_id,
            "kundali": kundali_data,
            **report,
        }
        session["report_status"] = "completed"
    except Exception as e:
        logger.error(f"Error generating report for {session_id}: {e}")
        session["report_status"] = "error"


@app.post("/api/onboarding/submit")
def submit_onboarding(submission: SurveySubmission, background_tasks: BackgroundTasks):
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
    
    # If both users have submitted, trigger the background report generation
    session = db["sessions"][session_id]
    if "user_a" in session and "prompt" in session["user_a"] and \
       "user_b" in session and "prompt" in session["user_b"]:
        
        # Only start if not already generating/completed
        if session.get("report_status") not in ["generating", "completed"]:
            session["report_status"] = "generating"
            background_tasks.add_task(generate_and_cache_report, session_id)
            print(f"Started background report generation for {session_id}")

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
def get_compatibility_report(req: CompatibilityRequest, response: Response, background_tasks: BackgroundTasks):
    session = db["sessions"].get(req.session_id, {})
    
    report_status = session.get("report_status", "pending")
    
    if report_status == "completed" and "cached_report" in session:
        return session["cached_report"]
    elif report_status == "generating":
        response.status_code = status.HTTP_202_ACCEPTED
        return {"status": "generating", "message": "The LLM is currently synthesizing the behavioral report."}
    elif report_status == "error":
        raise HTTPException(status_code=500, detail="An error occurred during report generation.")
    else:
        # Fallback: if somehow it wasn't triggered, start it now
        user_a_ready = "user_a" in session and "prompt" in session["user_a"]
        user_b_ready = "user_b" in session and "prompt" in session["user_b"]
        
        if user_a_ready and user_b_ready:
            session["report_status"] = "generating"
            background_tasks.add_task(generate_and_cache_report, req.session_id)
            response.status_code = status.HTTP_202_ACCEPTED
            return {"status": "generating", "message": "Started background report generation."}
        else:
            raise HTTPException(status_code=400, detail="Both users must complete onboarding before report generation.")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
