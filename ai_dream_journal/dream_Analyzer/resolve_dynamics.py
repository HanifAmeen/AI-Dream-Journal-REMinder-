import re
from symbol_emotion_map import SYMBOL_EMOTION_MAP

# ✅ STEP 1: EXPANDED Motion Detection
MOTION_VERBS = {
    "run","running","ran",
    "chase","chased",
    "escape","escaped",
    "follow","flee",
    "move","moving",
    "walk","walking",
    "fall","falling",
    "jump","jumped",
    "climb","climbing",
    "crawl",
    "approach",
    "rush",
    "hide"
}

def contains_word(text: str, word: str) -> bool:
    """Word-boundary safe word matching to prevent substring false positives"""
    return re.search(rf"\b{word}\b", text) is not None

def resolve_symbol_emotion_dynamics(insight: dict, dream_text: str):
    """
    Resolve dynamics only when symbol + emotion are text-supported.
    Enhanced with emotion fallback, symbol strength, structural detection,
    deduplication, late-narrative weighting, and word-boundary safety.
    """
    dominant_emotion = insight.get("dominant_emotion")
    symbol_scores = insight.get("symbol_scores", {})

    # 🔧 FIX: derive word_count directly
    word_count = len(dream_text.split())
    text = dream_text.lower()
    has_motion = any(contains_word(text, v) for v in MOTION_VERBS)

    # ✅ STEP 5: Late-narrative weighting
    words = text.split()
    last_third = words[int(len(words) * 0.66):]
    late_text = " ".join(last_third)

    dynamics = []

    # Main symbol-emotion loop with fallbacks
    for symbol, score in symbol_scores.items():
        # ✅ STEP 2: Stricter baseline threshold
        if score < 0.35:
            continue

        # ✅ STEP 1: Emotion fallback logic
        key = (symbol, dominant_emotion)
        if key in SYMBOL_EMOTION_MAP:
            mapping = SYMBOL_EMOTION_MAP[key]
        # Fallback: symbol-only mapping
        elif (symbol, None) in SYMBOL_EMOTION_MAP:
            mapping = SYMBOL_EMOTION_MAP[(symbol, None)]
        else:
            continue

        dynamic = mapping["dynamic"]

        # ✅ STEP 3: FIXED - Only pursuit/escape require motion
        if dynamic in {"pursuit", "escape"}:
            if not has_motion:
                continue

        # Short dream safety
        if word_count < 12 and score < 0.45:
            continue

        # ✅ STEP 2: Include symbol strength
        dynamics.append({
            "symbol": symbol,
            "emotion": dominant_emotion,
            "dynamic": dynamic,
            "focus": mapping["focus"],
            "strength": score  # NEW: Preserve intensity
        })

    # ✅ STEP 3: Structural threat detection (WORD-BOUNDARY SAFE ✅)
    confinement_words = ["trapped", "locked", "inside", "closed"]
    pursuit_words = ["chase", "chased", "pursued"]
    escape_words = ["escape", "exit", "outside"]

    has_confinement = any(contains_word(text, w) for w in confinement_words)
    has_pursuit_word = any(contains_word(text, w) for w in pursuit_words)
    has_escape_word = any(contains_word(text, w) for w in escape_words)

    # ✅ IMPROVEMENT 2: FIXED - Lower narrative strength to 0.45
    if has_pursuit_word:
        dynamics.append({
            "symbol": "narrative",
            "emotion": dominant_emotion,
            "dynamic": "pursuit",
            "focus": "threat",
            "strength": 0.45  # Lowered from 0.55
        })

    if has_confinement:
        dynamics.append({
            "symbol": "narrative",
            "emotion": dominant_emotion,
            "dynamic": "confinement",
            "focus": "restriction",
            "strength": 0.45  # Lowered from 0.55
        })

    if has_escape_word:
        dynamics.append({
            "symbol": "narrative",
            "emotion": dominant_emotion,
            "dynamic": "transition",
            "focus": "release",
            "strength": 0.45  # Lowered from 0.55
        })

    # ✅ STEP 5: Late-narrative resolution detection (WORD-BOUNDARY SAFE)
    resolution_words = ["safe", "outside", "relieved", "calm"]
    if any(contains_word(late_text, w) for w in resolution_words):
        dynamics.append({
            "symbol": "narrative",
            "emotion": dominant_emotion,
            "dynamic": "resolution_shift",
            "focus": "release",
            "strength": 0.45  # Lowered from 0.55
        })

    # ✅ STEP 4: Remove duplicate dynamics (keep strongest)
    unique = {}
    for d in dynamics:
        dyn = d["dynamic"]
        if dyn not in unique or d["strength"] > unique[dyn]["strength"]:
            unique[dyn] = d

    return list(unique.values())
