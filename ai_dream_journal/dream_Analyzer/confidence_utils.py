# confidence_utils.py

def compute_symbol_confidence(symbol_scores: dict, dream_text: str = None) -> float:
    """
    Score symbols using:
    - frequency of appearance (strong weight)
    - narrative position (smaller weight)

    The most important symbol will normalize to 1.0
    """

    if not symbol_scores:
        print("DEBUG SYMBOL CONF: No symbols detected")
        return 0.0

    tokens = dream_text.lower().split() if dream_text else []

    scored_symbols = {}

    for symbol in symbol_scores:

        # -----------------------------
        # Frequency weight (dominant)
        # -----------------------------
        freq = tokens.count(symbol)
        freq_weight = 1 + (freq * 0.8)

        # -----------------------------
        # Narrative position weight
        # -----------------------------
        if symbol in tokens:
            position = tokens.index(symbol) / len(tokens)
            position_weight = 1 - position
        else:
            position_weight = 0.5

        # -----------------------------
        # Combine weights
        # -----------------------------
        score = (freq_weight * 0.7) + (position_weight * 0.3)

        scored_symbols[symbol] = score

    # Normalize so highest = 1.0
    max_score = max(scored_symbols.values())

    normalized_scores = {
        sym: round(score / max_score, 3)
        for sym, score in scored_symbols.items()
    }

    sorted_symbols = sorted(
        normalized_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    print("\nDEBUG SYMBOL IMPORTANCE:")
    for sym, score in sorted_symbols:
        print(f"{sym}: {score:.2f}")

    # Average of top symbols
    avg_strength = sum(score for _, score in sorted_symbols[:5]) / min(len(sorted_symbols), 5)

    print(f"Symbol Confidence Score: {avg_strength:.3f}")

    return round(avg_strength, 3)


def compute_emotion_confidence(emotion_scores: dict) -> float:
    """
    Placeholder - implement your emotion confidence logic here.
    """
    return 0.0


def compute_overall_confidence(symbol_conf: float, emotion_conf: float, symbol_count: int) -> float:
    """
    Combine emotion certainty, symbol grounding, and narrative richness.
    """

    richness = min(symbol_count / 5, 1.0)

    combined = (
        emotion_conf * 0.5 +
        symbol_conf * 0.3 +
        richness * 0.2
    )

    overall_percentage = combined * 100

    print(f"\nDEBUG OVERALL CONFIDENCE: {overall_percentage:.2f}%")

    return round(min(1.0, max(0.0, combined)), 3)