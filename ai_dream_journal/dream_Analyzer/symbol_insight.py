def build_symbol_insight(
    symbol_scores: dict,
    dominant_emotion: str,
    dream_text: str,
    top_n: int = 3
):
    """
    Build a psychologically grounded symbol insight object.
    """

    # 🔍 DEBUG: inspect incoming symbol scores


    word_count = len(dream_text.split())

    # --- Threshold ---
    base_min_score = 0.25

    # --- Penalize abstraction for short dreams ---
    ABSTRACT_SYMBOLS = {
        "pursuit", "stagnation", "instability", "exposure",
        "pressure", "conflict", "avoidance", "threat"
    }

    adjusted_scores = {}
    for sym, score in symbol_scores.items():
        adjusted = score

        if sym in ABSTRACT_SYMBOLS and word_count < 20:
            adjusted *= 0.6

        if dominant_emotion == "neutral" and sym in ABSTRACT_SYMBOLS:
            adjusted *= 0.5

        adjusted_scores[sym] = adjusted

    # --- Rank symbols ---
    ranked = sorted(
        adjusted_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # --- Apply threshold ---
    filtered = [
        (sym, score) for sym, score in ranked
        if score >= base_min_score
    ][:top_n]

    if not filtered:
        return {
            "primary_symbol": None,
            "secondary_symbols": [],
            "symbol_scores": {},
            "dominant_emotion": dominant_emotion
        }

    primary = filtered[0][0]
    secondary = [s for s, _ in filtered[1:]]

    return {
        "primary_symbol": primary,
        "secondary_symbols": secondary,
        "symbol_scores": {
            s: round(score, 3) for s, score in filtered
        },
        "dominant_emotion": dominant_emotion
    }
