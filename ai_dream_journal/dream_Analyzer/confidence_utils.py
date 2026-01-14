# confidence_utils.py

def compute_symbol_confidence(symbol_scores: dict) -> float:
    """
    Confidence based on dominance of top symbol.
    Returns value in [0, 1].
    """
    if not symbol_scores or len(symbol_scores) < 2:
        return 0.0

    sorted_scores = sorted(symbol_scores.values(), reverse=True)
    top, second = sorted_scores[0], sorted_scores[1]

    return max(0.0, min(1.0, top - second))


# ⚠️ DEPRECATED — kept only for backward compatibility
def compute_emotion_confidence(emotion_scores: dict) -> float:
    """
    DO NOT USE.
    Emotion confidence is now computed inside emotion_detector.py
    """
    return 0.0


def compute_overall_confidence(symbol_conf: float, emotion_conf: float) -> float:
    """
    Combine symbol + emotion confidence.

    Emotion confidence is authoritative.
    Symbol confidence can enhance but must not suppress emotion.
    """

    # Preserve emotion signal
    combined = max(
        emotion_conf * 0.7,              # emotion alone
        (symbol_conf + emotion_conf) / 2 # blended
    )

    return round(min(1.0, max(0.0, combined)), 3)
