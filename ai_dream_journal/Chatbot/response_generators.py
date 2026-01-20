import random

# ------------------------------
# HOME PAGE RESPONSES
# ------------------------------

def answer_generic_dream_question(user_message):
    if "fall" in user_message.lower():
        return (
            "Dreams about falling often relate to loss of control or instability. "
            "They’re common during stress or uncertainty, especially when something "
            "in waking life feels out of your hands."
        )

    return (
        "Dreams often reflect emotional concerns rather than literal events. "
        "Patterns, emotions, and repetition usually matter more than exact symbols."
    )


# ------------------------------
# INPUT PAGE (CLARIFICATION)
# ------------------------------

CLARIFY_QUESTIONS = [
    "How did the dream end emotionally?",
    "Were you alone or with someone you know?",
    "Did the fear stay constant or spike suddenly?",
    "Was there a moment that stood out the most?"
]

def ask_clarifying_question():
    return random.choice(CLARIFY_QUESTIONS)


# ------------------------------
# ANALYSIS PAGE (INSIGHT)
# ------------------------------

def generate_analysis_insight(symbols, dominant_emotion):
    if dominant_emotion == "anxiety":
        return (
            "The anxiety in this dream seems tied to evaluation or pressure. "
            "Symbols like exposure and authority often appear when someone feels "
            "judged or unprepared in waking life."
        )

    if "authority" in symbols:
        return (
            "Authority figures in dreams often represent internal pressure rather "
            "than real people — expectations you feel you must meet."
        )

    return (
        "This dream appears to reflect an unresolved emotional situation rather "
        "than a specific external event."
    )
