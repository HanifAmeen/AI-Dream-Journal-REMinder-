from sentence_transformers import SentenceTransformer
from emotion_definitions import EMOTION_DEFINITIONS
import re
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from collections import Counter

# ------------------------------
# Ensure NLTK punkt is available
# ------------------------------
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# ------------------------------
# Model loading
# ------------------------------
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Pre-embed emotion definitions
_EMOTION_EMBEDDINGS = {
    emotion: _model.encode(text, normalize_embeddings=True)
    for emotion, text in EMOTION_DEFINITIONS.items()
}

# ------------------------------
# Emotion normalization constants
# ------------------------------
EMOTION_GROUPS = {
    # Fear cluster
    "anxiety": "fear",
    "panic": "fear",
    "terror": "fear",
    "dread": "fear",

    # Sadness cluster
    "shame": "sadness",
    "guilt": "sadness",
    "regret": "sadness",

    # Calm / safety cluster
    "relief": "calm",
    "peace": "calm",
    "comfort": "calm",

    # Surprise cluster
    "shock": "surprise",
    "astonishment": "surprise",

    # Joy cluster
    "happiness": "joy",
    "delight": "joy"
}

EMOTION_DISPLAY = {
    "fear": "fear",
    "anger": "anger",
    "sadness": "sadness",
    "disgust": "disgust",
    "surprise": "surprise",
    "joy": "joy",
    "trust": "trust",
    "anticipation": "anticipation",
    "anxiety": "anxiety",
    "calm": "calmness",
    "neutral": "neutrality",
    "shame": "shame"
}

# ------------------------------
# Constants
# ------------------------------
NEUTRAL_EMOTION = "neutral"
SHORT_TEXT_PENALTY = 0.75

# 🔥 STEP 1: EMOTIONAL METADATA (Enhanced)
EMOTION_META = {
    "fear":        {"valence": -1, "arousal": 0.9, "threat": 1.0},
    "anger":       {"valence": -1, "arousal": 0.8, "threat": 0.8},
    "shame":       {"valence": -1, "arousal": 0.6, "threat": 0.6},
    "disgust":     {"valence": -1, "arousal": 0.7, "threat": 0.6},
    "sadness":     {"valence": -1, "arousal": 0.4, "threat": 0.3},
    "surprise":    {"valence":  0, "arousal": 0.7, "threat": 0.2},
    "anticipation": {"valence":  0, "arousal": 0.5, "threat": 0.2},
    "joy":         {"valence":  1, "arousal": 0.6, "threat": 0.0},
    "calm":        {"valence":  1, "arousal": 0.2, "threat": 0.0},
    "trust":       {"valence":  1, "arousal": 0.3, "threat": 0.0},
    "neutral":     {"valence":  0, "arousal": 0.1, "threat": 0.0},
    "anxiety":     {"valence": -1, "arousal": 0.85, "threat": 0.9},
}

# 🔥 STEP 4: Enhanced Explicit Emotion Vocabulary
EXPLICIT_EMOTION_WORDS = {
    "joy": {"happy", "joy", "excited", "pleased", "delighted", "content", "relieved"},
    "sadness": {"sad", "cry", "lonely", "grief", "depressed", "lost"},
    "fear": {
        "scared", "afraid", "terrified", "fear", "panic",
        "uneasy", "tense", "anxious", "worried"
    },
    "anger": {"angry", "furious", "rage", "mad"},
    "calm": {"calm", "peaceful", "relaxed", "serene", "steady"},
    "disgust": {"disgusted", "gross", "dirty", "nasty", "rotten"},
    "surprise": {"surprised", "shocked", "suddenly", "unexpected"},
    "trust": {"trusted", "safe", "protected", "secure"},
    "anticipation": {"waiting", "expecting", "anticipate", "hoping"},
    "shame": {"ashamed", "embarrassed", "humiliated", "exposed"},
    "anxiety": {"worried", "nervous", "stressed", "overwhelmed"},
}

# 🔥 NEW: Environmental Emotion Cues
ENVIRONMENTAL_EMOTIONS = {
    "fear": {
        "dark", "night", "shadow", "forest", "unknown",
        "chasing", "monster", "trap", "danger",
        "falling", "edge", "cliff", "lost", "alone",
        "abandoned", "basement", "maze", "labyrinth"
    },
    "sadness": {
        "empty", "abandoned", "ruins", "broken",
        "rain", "storm", "grave", "funeral",
        "old", "dust", "decay", "lost",
        "farewell", "leaving", "missing"
    },
    "calm": {
        "quiet", "still", "peaceful", "lake",
        "meadow", "sunlight", "breeze",
        "garden", "soft", "warm",
        "safe", "home", "floating"
    },
    "joy": {
        "celebration", "festival", "music",
        "dancing", "friends", "laughter",
        "light", "golden", "gift",
        "flying", "freedom"
    },
    "surprise": {
        "suddenly", "unexpected", "appeared",
        "vanished", "transformed", "shifted",
        "opened", "revealed"
    },
    "anxiety": {
        "late", "missed", "exam", "school",
        "crowd", "running", "searching",
        "waiting", "deadline", "pressure"
    }
}

NEGATION_WORDS = {"not", "never", "no", "without", "hardly", "barely"}
CONTRAST_WORDS = {"but", "rather", "instead", "though", "although", "however"}
FEAR_WORDS = {"afraid", "scared", "fearful", "terrified", "anxious", "panic"}
POSITIVE_STATE_WORDS = {"safe", "calm", "peaceful", "relaxed", "secure", "curious"}
INTENSIFIERS = {"very", "extremely", "really", "so", "too", "quite", "deeply"}

WINDOW = 4
EMOTION_ACCEPT_THRESHOLD = 0.28
IMPLICIT_MAX_CONF = 0.55
EXPLICIT_MAX_CONF = 0.75
ENVIRONMENTAL_WEIGHT = 0.12

# ------------------------------
# 🔥 FIXED: Core emotion detection (emotion grouping AT RETURN)
# ------------------------------
def detect_emotion_with_scores(dream_text: str):
    if not dream_text:
        return NEUTRAL_EMOTION, {}, 0.1

    text = dream_text.lower()
    tokens_list = re.findall(r"\b\w+\b", text)
    tokens_set = set(tokens_list)
    word_count = len(tokens_list)

    # Negation / contrast handling
    for i, token in enumerate(tokens_list):
        if token in FEAR_WORDS:
            left = tokens_list[max(0, i - WINDOW):i]
            right = tokens_list[i + 1:i + 1 + WINDOW]

            if (
                any(w in NEGATION_WORDS for w in left)
                or any(w in CONTRAST_WORDS for w in left)
                or any(w in POSITIVE_STATE_WORDS for w in right)
            ):
                confidence = 0.5 + 0.08 * sum(
                    1 for w in POSITIVE_STATE_WORDS if w in tokens_set
                )
                return "calm", {}, min(confidence, EXPLICIT_MAX_CONF)

    # SCORING-BASED EXPLICIT EMOTION
    explicit_scores = {}
    for emotion, words in EXPLICIT_EMOTION_WORDS.items():
        matched = tokens_set & words
        if matched:
            score = 0.45 + 0.08 * len(matched)
            for i, token in enumerate(tokens_list):
                if token in matched:
                    left = tokens_list[max(0, i - 2):i]
                    if any(w in INTENSIFIERS for w in left):
                        score += 0.08
            explicit_scores[emotion] = score

    if explicit_scores:
        best_emotion = max(explicit_scores, key=explicit_scores.get)
        # ✅ FIX 1: Normalize explicit emotions too
        best_emotion = EMOTION_GROUPS.get(best_emotion, best_emotion)
        return best_emotion, explicit_scores, min(explicit_scores[max(explicit_scores, key=explicit_scores.get)], EXPLICIT_MAX_CONF)

    # Very short dreams
    if word_count < 6:
        return NEUTRAL_EMOTION, {}, 0.15

    # ENVIRONMENTAL EMOTION BOOST
    env_scores = {}
    for emotion, words in ENVIRONMENTAL_EMOTIONS.items():
        matches = tokens_set & words
        if matches:
            env_scores[emotion] = min(len(matches), 3) * ENVIRONMENTAL_WEIGHT

    # SBERT implicit emotion
    dream_embedding = _model.encode(dream_text, normalize_embeddings=True)
    raw_scores = {
        emotion: float(dream_embedding @ emb)
        for emotion, emb in _EMOTION_EMBEDDINGS.items()
    }

    # Add environmental boost to raw scores
    for emotion, score in env_scores.items():
        raw_scores[emotion] = raw_scores.get(emotion, 0) + score

    ranked = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    top_emotion, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0

    if top_score < 0.22:
        return NEUTRAL_EMOTION, raw_scores, 0.15

    confidence = 0.18 + (top_score - second_score) * 1.5
    if word_count < 20:
        confidence *= SHORT_TEXT_PENALTY

    confidence = min(confidence, IMPLICIT_MAX_CONF)

    if confidence < EMOTION_ACCEPT_THRESHOLD:
        return NEUTRAL_EMOTION, raw_scores, confidence

    # ✅ FIX 1: Normalize ALL detected emotions (including SBERT)
    top_emotion = EMOTION_GROUPS.get(top_emotion, top_emotion)
    return top_emotion, raw_scores, confidence

# ------------------------------
# 🔥 IMPROVED: Trajectory verbalizer (3-emotion special case)
# ------------------------------
def verbalize_emotion_trajectory(trajectory):
    if not trajectory:
        return "The emotional direction of the dream is unclear."

    display = [EMOTION_DISPLAY.get(e, e) for e in trajectory]

    if len(display) == 1:
        return f"The dream remains emotionally centered around {display[0]}."

    if len(display) == 2:
        return f"The dream begins with {display[0]} and shifts toward {display[1]}."

    if len(display) == 3:
        return f"The dream begins with {display[0]}, shifts through {display[1]}, and ends with {display[2]}."

    middle = ", then ".join(display[1:-1])
    return (
        f"The dream begins with {display[0]}, "
        f"then transitions through {middle}, "
        f"and ends with {display[-1]}."
    )

# ------------------------------
# 🔥 FIXED: Emotion trajectory detection (improved smoothing + fallback fix)
# ------------------------------
def detect_emotion_trajectory(dream_text: str):
    if not dream_text:
        return {
            "overall_emotion": NEUTRAL_EMOTION,
            "overall_confidence": 0.1,
            "trajectory": [],
            "trajectory_description": "The emotional direction of the dream is unclear.",
            "shift_intensity": "none",
        }

    # Scene-based splitting with safe fallback
    try:
        from scene_splitter import split_into_scenes
        sentences = [s.strip() for s in split_into_scenes(dream_text) if s.strip()]
    except:
        sentences = [s.strip() for s in sent_tokenize(dream_text) if s.strip()]

    emotions = []
    confidences = []

    for s in sentences:
        emo, raw_scores, conf = detect_emotion_with_scores(s)
        
        if emo != NEUTRAL_EMOTION:
            emotions.append(emo)
            confidences.append(conf)
        elif raw_scores:
            # ✅ FIX 2: Normalize raw_scores before selecting best
            normalized_scores = {
                EMOTION_GROUPS.get(e, e): v
                for e, v in raw_scores.items()
            }
            best = max(normalized_scores, key=normalized_scores.get)
            emotions.append(best)
            confidences.append(normalized_scores[best])
        else:
            emotions.append(NEUTRAL_EMOTION)
            confidences.append(conf)

    # ✅ FIX 3: Improved spike smoothing
    trajectory = []
    for i, emo in enumerate(emotions):
        if not trajectory:
            trajectory.append(emo)
            continue

        prev = emotions[i-1] if i > 0 else None
        next_ = emotions[i+1] if i < len(emotions)-1 else None

        # Remove spikes (prev == next_ != current)
        if prev and next_ and prev == next_ and emo != prev:
            continue

        if emo != trajectory[-1]:
            trajectory.append(emo)

    # Limit trajectory length to 5 max
    if len(trajectory) > 5:
        trajectory = trajectory[:5]

    # Remove isolated neutral noise
    if len(trajectory) > 2:
        cleaned = [emo for emo in trajectory if emo != NEUTRAL_EMOTION]
        if cleaned:
            trajectory = cleaned
            if not trajectory:
                trajectory = [NEUTRAL_EMOTION]

    unique_count = len(set(trajectory))
    shift_intensity = (
        "none" if unique_count <= 1 else
        "mild" if unique_count == 2 else
        "moderate" if unique_count == 3 else
        "strong"
    )

    # NARRATIVE-WEIGHTED DOMINANCE (unchanged)
    emotion_counts = Counter(trajectory)
    if NEUTRAL_EMOTION in emotion_counts and len(emotion_counts) > 1:
        del emotion_counts[NEUTRAL_EMOTION]

    emotion_strength = {}
    for emo in emotion_counts.keys():
        indices = [i for i, e in enumerate(emotions) if e == emo]
        if not indices:
            continue

        avg_conf = np.mean([confidences[i] for i in indices])
        freq = len(indices)
        meta = EMOTION_META.get(emo, {"valence":0, "arousal":0.5, "threat":0})

        base = (0.35 * freq) + (0.35 * avg_conf)
        arousal_weight = meta["arousal"] * 0.4
        threat_weight = meta["threat"] * 0.6
        position_weight = sum(
            (1 - (i / len(emotions))) for i in indices
        ) * 0.25

        emotion_strength[emo] = base + arousal_weight + threat_weight + position_weight

    # VALENCE-AWARE SCALING
    for emo in emotion_strength:
        meta = EMOTION_META.get(emo, {})
        if meta.get("valence") == -1:
            emotion_strength[emo] *= 1.15
        elif meta.get("valence") == 1:
            emotion_strength[emo] *= 0.95

    # Normalize emotion strengths
    if emotion_strength:
        total_strength = sum(emotion_strength.values())
        emotion_distribution = {
            emo: round((score / total_strength), 4)
            for emo, score in emotion_strength.items()
        }
        emotion_distribution = dict(
            sorted(emotion_distribution.items(), key=lambda x: x[1], reverse=True)
        )
    else:
        emotion_distribution = {}

    dominant = max(emotion_strength.items(), key=lambda x: x[1])[0] if emotion_strength else NEUTRAL_EMOTION
    overall_conf = max(confidences) if confidences else 0.1

    return {
        "overall_emotion": dominant,
        "overall_confidence": round(float(overall_conf), 3),
        "emotion_distribution": emotion_distribution,
        "trajectory": trajectory,
        "trajectory_description": verbalize_emotion_trajectory(trajectory),
        "shift_intensity": shift_intensity,
    }
