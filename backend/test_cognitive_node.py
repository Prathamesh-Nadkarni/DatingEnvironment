import json
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from state_models import PersonaContext, TraitDistribution

from langchain_core.output_parsers import PydanticOutputParser

# Define the structured output schema for the Cognitive Engine
class CognitiveEvaluation(BaseModel):
    perception: str = Field(description="What the person believes bothers them most about the situation.")
    emotion: str = Field(description="What the person feels first (e.g., anxiety, anger, shame).")
    impulse: str = Field(description="What the person instinctively wants to do (Reactive Policy).")
    action: str = Field(description="What the person actually chooses to do (Deliberative Policy applied).")
    divergence_reason: str = Field(description="Why the impulse and action differ (if they do), based on values/traits.")
    history_impact: str = Field(description="How previous unresolved history would change their next choice.")

# Setup Ollama model with structured output parser
llm = ChatOllama(model="llama3.1", temperature=0, format="json")
parser = PydanticOutputParser(pydantic_object=CognitiveEvaluation)

def evaluate_scenario(persona: PersonaContext, scenario: str, history: str) -> CognitiveEvaluation:
    prompt = PromptTemplate(
        template="""You are the cognitive engine for a simulated relationship persona.
        
Given the following scenario, determine the persona's internal cognitive state and chosen action.

Scenario: {scenario}

Persona Traits:
- Family Deference: {family_deference}
- Partner Advocacy: {partner_advocacy}
- Threat Sensitivity: {threat_sensitivity}
- Impulse Control: {impulse_control}

Behavioral Policies:
- Reactive vs Deliberative (0=Reactive, 1=Deliberative): {reactive_deliberative}
- Self Protect vs Relationship Protect (0=Self, 1=Relationship): {protect_policy}

Relationship History:
{history}

{format_instructions}
""",
        input_variables=["scenario", "family_deference", "partner_advocacy", "threat_sensitivity", "impulse_control", "reactive_deliberative", "protect_policy", "history"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser

    
    result = chain.invoke({
        "scenario": scenario,
        "family_deference": persona.relationship_traits.get("family_deference", TraitDistribution(mean=0.5, confidence=0.0)).mean,
        "partner_advocacy": persona.relationship_traits.get("partner_advocacy", TraitDistribution(mean=0.5, confidence=0.0)).mean,
        "threat_sensitivity": persona.threat_sensitivity,
        "impulse_control": persona.impulse_control,
        "reactive_deliberative": persona.reactive_vs_deliberative,
        "protect_policy": persona.self_protect_vs_relationship_protect,
        "history": history
    })
    
    return result

if __name__ == "__main__":
    # Test Persona (High advocacy, high deference, high shame/threat sensitivity)
    persona = PersonaContext(
        relationship_traits={
            "family_deference": TraitDistribution(mean=0.8, confidence=0.9),
            "partner_advocacy": TraitDistribution(mean=0.8, confidence=0.9)
        },
        threat_sensitivity=0.9,
        impulse_control=0.7,
        reactive_vs_deliberative=0.8, # Highly deliberative
        self_protect_vs_relationship_protect=0.7 # Protects relationship
    )
    
    scenario = "Your mother publicly criticizes your spouse's cooking at a family dinner in front of 10 relatives."
    history = "Unresolved Hurt: The spouse previously felt abandoned when you stayed silent during a similar incident 3 months ago."
    
    print("Running Milestone Cognitive Evaluation...\n")
    evaluation = evaluate_scenario(persona, scenario, history)
    
    print(json.dumps(evaluation.model_dump(), indent=2))
