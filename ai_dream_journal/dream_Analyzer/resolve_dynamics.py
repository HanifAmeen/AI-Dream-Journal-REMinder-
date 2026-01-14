from symbol_emotion_map import SYMBOL_EMOTION_MAP

MOTION_VERBS = {
    "run", "chase", "escape", "follow", "flee",
    "move", "walk", "fall", "hide", "approach"
}

def resolve_symbol_emotion_dynamics(insight: dict, dream_text: str):
    """
    Resolve dynamics only when symbol + emotion are text-supported.
    """

    dominant_emotion = insight.get("dominant_emotion")
    symbol_scores = insight.get("symbol_scores", {})

    # 🔧 FIX: derive word_count directly (meta was never provided)
    word_count = len(dream_text.split())

    text = dream_text.lower()
    has_motion = any(v in text for v in MOTION_VERBS)

    dynamics = []

    for symbol, score in symbol_scores.items():

        # Weak symbol → no dynamics
        if score < 0.3:
            continue

        key = (symbol, dominant_emotion)
        if key not in SYMBOL_EMOTION_MAP:
            continue

        dynamic = SYMBOL_EMOTION_MAP[key]["dynamic"]

        # Evidence gate: motion dynamics need motion text
        if dynamic in {"pursuit", "escape", "pressure", "instability"}:
            if not has_motion:
                continue

        # Short dream safety (NOW WORKS AS INTENDED)
        if word_count < 12 and score < 0.45:
            continue

        dynamics.append({
            "symbol": symbol,
            "emotion": dominant_emotion,
            "dynamic": dynamic,
            "focus": SYMBOL_EMOTION_MAP[key]["focus"]
        })

    return dynamics
