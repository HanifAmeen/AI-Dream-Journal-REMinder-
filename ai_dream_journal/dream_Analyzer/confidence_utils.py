# confidence_utils.py

def compute_symbol_confidence(symbol_scores: dict) -> float:
    """
    Convert raw symbol strengths into a confidence score.
    Uses the average strength of the top symbols.
    """
    if not symbol_scores:
        print("DEBUG SYMBOL CONF: No symbols detected")
        return 0.0

    # sort symbols by strength
    sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)

    # take top 5
    top_symbols = sorted_symbols[:5]

    # average raw score
    avg_strength = sum(score for _, score in top_symbols) / len(top_symbols)

    # normalize into 0–1 range
    symbol_conf = min(avg_strength / 2.0, 1.0)

    print("\nDEBUG SYMBOL CONFIDENCE:")
    for sym, score in top_symbols:
        print(f"{sym}: {score:.2f}")

    print(f"Symbol Confidence Score: {symbol_conf:.3f}")

    return round(symbol_conf, 3)


def compute_emotion_confidence(emotion_scores: dict) -> float:
    """
    Placeholder - implement your emotion confidence logic here.
    """
    # Your existing emotion confidence implementation
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
