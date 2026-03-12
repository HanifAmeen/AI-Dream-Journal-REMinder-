import re
from nltk.stem import WordNetLemmatizer

def build_symbol_insight(
    symbol_scores: dict,
    dominant_emotion: str,
    dream_text: str,
    top_n: int = 12
):
    """
    Build a psychologically grounded symbol insight object.
    """

    print(f"DEBUG: Incoming symbol_scores: {symbol_scores}")

    # --- Config ---
    base_min_score = 0.40          # ✅ Keep as is - healthy cutoff
    strong_similarity = 0.60       # Strong semantic override threshold
    gap_threshold = 0.06           # Slightly safer separation margin

    HIGH_RISK_SYMBOLS = {
        "naked_in_public",
        "bleeding",
        "drowning",
        "attack",
        "death"
    }

    ABSTRACT_SYMBOLS = {
        "pursuit", "stagnation", "instability", "exposure",
        "pressure", "conflict", "avoidance", "threat"
    }

    # --- Preprocess dream text with lemmatization ---
    dream_lower = dream_text.lower()
    lemmatizer = WordNetLemmatizer()

    dream_tokens = [
        lemmatizer.lemmatize(w)
        for w in re.findall(r'\b\w+\b', dream_lower)
    ]

    word_count = len(dream_tokens)

    # --- Adjust scores ---
    adjusted_scores = {}

    for sym, score in symbol_scores.items():
        adjusted = score

        # Penalize abstract symbols in short dreams ✅ Keep as is
        if sym in ABSTRACT_SYMBOLS and word_count < 20:
            adjusted *= 0.6

        if dominant_emotion == "neutral" and sym in ABSTRACT_SYMBOLS:
            adjusted *= 0.5

        adjusted_scores[sym] = adjusted

    # --- Sort by score ---
    ranked = sorted(
        adjusted_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # --- Grounding Filter ---
    grounded = []

    for sym, score in ranked:
        sym_clean = sym.replace("_", " ")
        sym_lemma = lemmatizer.lemmatize(sym_clean)

        # ✅ STEP 2: FIXED High-risk symbol detection (flexible matching)
        if sym in HIGH_RISK_SYMBOLS:
            if not any(word in dream_tokens for word in sym_clean.split()):
                continue

        # Accept if strongly similar
        if score >= strong_similarity:
            grounded.append((sym, score))
            continue

        # Accept if lexically grounded (lemmatized match)
        if sym_lemma in dream_tokens:
            grounded.append((sym, score))

    # --- Apply base threshold AFTER grounding ---
    grounded = [
        (sym, score)
        for sym, score in grounded
        if score >= base_min_score
    ]

    if not grounded:
        return {
            "primary_symbol": None,
            "secondary_symbols": [],
            "symbol_scores": {},
            "dominant_emotion": dominant_emotion
        }

    # ✅ STEP 1: FIXED - Collapse to 2 instead of 1 (keep multiple strong symbols)
    if len(grounded) >= 3:
        if grounded[0][1] - grounded[2][1] < gap_threshold:
            grounded = grounded[:2]  # Changed from [:1] to [:2]

    # --- Limit to top_n ---
    filtered = grounded[:top_n]

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
