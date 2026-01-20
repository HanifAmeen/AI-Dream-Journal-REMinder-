SYMBOL_FOLLOWUPS = {
    "authority": "Did the authority figure feel threatening or disappointing?",
    "exposure": "What were you afraid others would notice?",
    "lateness": "Is there something in waking life you feel unprepared for?",
    "chase": "What do you think would have happened if you stopped running?"
}

GENERIC_FOLLOWUPS = [
    "Does this dream connect to anything currently stressing you?",
    "Which part of the dream felt most intense?",
    "Did the emotion change at any point in the dream?"
]


def choose_followup_question(symbols):
    for s in symbols:
        if s in SYMBOL_FOLLOWUPS:
            return SYMBOL_FOLLOWUPS[s]

    return GENERIC_FOLLOWUPS[0]
