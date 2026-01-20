from enum import Enum

class PageMode(str, Enum):
    HOME = "home"
    INPUT = "input"
    ANALYSIS = "analysis"
    HISTORY = "history"


class Intent(str, Enum):
    GENERIC_QUESTION = "generic_question"
    CLARIFY_DREAM = "clarify_dream"
    EXPLAIN_SYMBOL = "explain_symbol"
    FOLLOW_UP_REFLECTION = "follow_up_reflection"
    PATTERN_INSIGHT = "pattern_insight"
