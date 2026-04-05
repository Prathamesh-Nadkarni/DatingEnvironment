# backend/sjt_seed_data.py

SJT_QUESTIONS = [
    {
        "id": "q1",
        "context_type": "Family Dynamics & Boundaries",
        "scenario_text": "Your mother insists your new wife must cook dinner every night, but your wife works 10-hour corporate shifts. How do you actually handle this?",
        "options": [
            {"id": "A", "text": "Ask your wife to compromise and cook simple meals to keep peace."},
            {"id": "B", "text": "Hire a cook secretly or explicitly against your mother's wishes."},
            {"id": "C", "text": "Tell your mother directly that her expectation is unrealistic and you will both manage the cooking."},
            {"id": "D", "text": "Take over the cooking entirely yourself to shield your wife."}
        ]
    },
    {
        "id": "q2",
        "context_type": "Financial Mutuality",
        "scenario_text": "Your partner allocates 20% of their salary strictly to support their retired parents, shrinking your joint saving capacity for a home. What is your internal reaction?",
        "options": [
            {"id": "A", "text": "Resentment; our new family unit and future home should be the absolute priority."},
            {"id": "B", "text": "Acceptance, provided they don't ask me to compromise my personal discretionary spending."},
            {"id": "C", "text": "Supportive mutuality; taking care of elder parents is a joint moral obligation we share equally."}
        ]
    },
    {
        "id": "q3",
        "context_type": "Egalitarianism vs Latent Patriarchy",
        "scenario_text": "Both of you return exhausted from a 9-to-5 job to a remarkably messy house, and guests are arriving in an hour. What instinct kicks in?",
        "options": [
            {"id": "A", "text": "I immediately start cleaning while expecting my partner to naturally help without asking."},
            {"id": "B", "text": "I wait for my partner to direct me on what needs to be done."},
            {"id": "C", "text": "I feel it's primarily my partner's responsibility to manage the household image."},
            {"id": "D", "text": "I suggest we order food or restructure the plan so neither of us has to clean right now."}
        ]
    }
]

def get_seed_data():
    return SJT_QUESTIONS
