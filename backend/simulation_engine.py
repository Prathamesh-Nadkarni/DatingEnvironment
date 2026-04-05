from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class SimulationState(TypedDict):
    agent_a_prompt: str
    agent_b_prompt: str
    scenario_details: dict
    dialogue_history: List[Dict[str, str]]
    turn_count: int
    max_turns: int
    current_speaker: str

def scene_master(state: SimulationState):
    """
    Injects the scenario into the state and sets the stage for Agent A.
    """
    scenario = state["scenario_details"]
    intro = f"SCENARIO START: {scenario.get('title', 'Unknown')}\n"
    intro += f"Details: {scenario.get('description', '')}\n"
    intro += f"Core Stressor: {scenario.get('test_reason', '')}\n"
    intro += f"Simulation Mechanic: {scenario.get('mechanic', '')}\n"
    
    state["dialogue_history"].append({
        "speaker": "Scene Master",
        "message": intro
    })
    state["current_speaker"] = "Agent A"
    return state

def agent_a_node(state: SimulationState):
    """
    Simulates Agent A's response using MiroFish Inner Parliament prompt.
    """
    history = state["dialogue_history"]
    persona_prompt = state["agent_a_prompt"]
    
    # Simulate internal conflict based on prompt cues
    if "family_deference" in persona_prompt and "0.7" in persona_prompt:
        thought = "<InternalThought>I feel a deep pressure to respect my elders, but I am worried about our relationship's autonomy. I'll try to be diplomatic but I might fold if the pressure increases.</InternalThought>"
        message = "I understand what my parents are saying, and I really want us to keep their trust. Maybe we can try what they suggest just for this time?"
    elif "egalitarianism" in persona_prompt and "0.7" in persona_prompt:
        thought = "<InternalThought>This is fundamentally unfair. I expect us to be equals and I won't stand for this traditional imbalance. I need to be firm.</InternalThought>"
        message = "I don't think that's a fair expectation at all. We both work hard, and we decided to build this home together. We should stick to our agreement regardless of what others expect."
    else:
        thought = "<InternalThought>I'm weighing the practical needs against our emotional connection.</InternalThought>"
        message = "Let's look at this practically. What's the best long-term move for us as a couple?"

    state["dialogue_history"].append({
        "speaker": "Agent A",
        "message": f"{thought}\n{message}"
    })
    state["current_speaker"] = "Agent B"
    return state

def agent_b_node(state: SimulationState):
    """
    Simulates Agent B's response using MiroFish Inner Parliament prompt.
    """
    history = state["dialogue_history"]
    persona_prompt = state["agent_b_prompt"]

    # Simple logic to simulate interaction for demo
    thought = "<InternalThought>I need to respond to their point while protecting my own boundaries.</InternalThought>"
    message = "I hear you. But how do we handle the emotional toll this takes? We need a solution that protects our peace too."

    state["dialogue_history"].append({
        "speaker": "Agent B",
        "message": f"{thought}\n{message}"
    })
    state["current_speaker"] = "Agent A"
    state["turn_count"] += 1
    return state

def controller_edge(state: SimulationState) -> str:
    """
    Determines if the simulation continues based on turn count.
    """
    if state["turn_count"] >= state["max_turns"]:
        return END
    
    if state["current_speaker"] == "Agent A":
        return "agent_a"
    else:
        return "agent_b"

# Build Graph
builder = StateGraph(SimulationState)

builder.add_node("scene_master", scene_master)
builder.add_node("agent_a", agent_a_node)
builder.add_node("agent_b", agent_b_node)

builder.add_edge(START, "scene_master")
builder.add_edge("scene_master", "agent_a")

builder.add_conditional_edges(
    "agent_a",
    controller_edge,
    {"agent_b": "agent_b", END: END}
)

builder.add_conditional_edges(
    "agent_b",
    controller_edge,
    {"agent_a": "agent_a", END: END}
)

simulation_graph = builder.compile()

def run_simulation(agent_a_prompt: str, agent_b_prompt: str, scenario: dict, max_turns: int = 5):
    initial_state = {
        "agent_a_prompt": agent_a_prompt,
        "agent_b_prompt": agent_b_prompt,
        "scenario_details": scenario,
        "dialogue_history": [],
        "turn_count": 0,
        "max_turns": max_turns,
        "current_speaker": "Scene Master"
    }
    
    final_state = simulation_graph.invoke(initial_state)
    return final_state
