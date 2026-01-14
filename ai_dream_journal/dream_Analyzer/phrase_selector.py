# phrase_selector.py

def select_phrase(phrases: list, index: int) -> str:
    """
    Deterministically select a phrase from a pool.
    Ensures variation without randomness.
    """
    if not phrases:
        return ""
    return phrases[index % len(phrases)]
