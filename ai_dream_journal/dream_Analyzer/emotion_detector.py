from sentence_transformers import SentenceTransformer
from emotion_definitions import EMOTION_DEFINITIONS
import re
import nltk
import numpy as np
import pandas as pd  # ADDED
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
# Load NRC Emotion Lexicon  # ADDED
# ------------------------------
NRC_PATH = r"C:\Users\amjad\Downloads\Research Papers 2025\Dream Journal\AI -Dream Journal APP\ai_dream_journal\datasets\NRC_cleaned_emotions.csv"

df_nrc = pd.read_csv(NRC_PATH)

# Convert NRC dataset into emotion -> word set dictionary
EXPLICIT_EMOTION_WORDS = {}

for emotion in df_nrc.columns[1:]:  # skip "word"
    EXPLICIT_EMOTION_WORDS[emotion.lower()] = set(
        df_nrc[df_nrc[emotion] == 1]["word"].str.lower()
    )

# Performance optimization
ALL_NRC_WORDS = set().union(*EXPLICIT_EMOTION_WORDS.values())

print("Loaded NRC emotion lexicon.")


# ------------------------------
# Constants
# ------------------------------
NEUTRAL_EMOTION = "neutral"
SHORT_TEXT_PENALTY = 0.75  


#  STEP 1: EMOTIONAL METADATA (Enhanced)
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
    "anxiety":     {"valence": -1, "arousal": 0.85, "threat": 0.9},  # NEW
}


# 🔥 NEW: Environmental Emotion Cues (Most Important Addition)
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
ENVIRONMENTAL_WEIGHT = 0.18  


# ------------------------------
#  Core emotion detection 
# ------------------------------
def detect_emotion_with_scores(dream_text: str):
    if not dream_text:
        return NEUTRAL_EMOTION, {}, 0.1


    text = dream_text.lower()
    # FIXED: Added .lower() normalization + fixed regex escape
    tokens_list = [w.lower() for w in re.findall(r"\b\w+\b", text)]
    # OPTIMIZED: Quick NRC word filter first
    tokens_set = set(tokens_list) & ALL_NRC_WORDS
    word_count = len(tokens_list)


    # Negation / contrast handling (unchanged)
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


    # 🔥 NEW: SCORING-BASED EXPLICIT EMOTION (NRC-POWERED)
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
        # ✅ STEP 1: FIXED - Pass explicit_scores instead of empty dict
        return best_emotion, explicit_scores, min(explicit_scores[best_emotion], EXPLICIT_MAX_CONF)


    # Very short dreams
    if word_count < 6:
        return NEUTRAL_EMOTION, {}, 0.15


    # 🔥 NEW: ENVIRONMENTAL EMOTION BOOST
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


    return top_emotion, raw_scores, confidence


# ------------------------------
# Trajectory verbalizer (UNCHANGED)
# ------------------------------
def verbalize_emotion_trajectory(trajectory):
    if not trajectory:
        return "The emotional direction of the dream is unclear."


    if len(trajectory) == 1:
        return f"The dream remains emotionally centered around {trajectory[0]}."


    if len(trajectory) == 2:
        return f"The dream starts with {trajectory[0]} and shifts toward {trajectory[1]}."


    middle = ", then ".join(trajectory[1:-1])
    return (
        f"The dream starts with {trajectory[0]}, "
        f"then shows signs of {middle}, "
        f"and ends with {trajectory[-1]}."
    )


# ------------------------------
# 🔥 UPDATED: Emotion trajectory detection (FULLY ROBUST)
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


    sentences = [s.strip() for s in sent_tokenize(dream_text) if s.strip()]


    emotions = []
    confidences = []


    for s in sentences:
        emo, raw_scores, conf = detect_emotion_with_scores(s)
        if emo != NEUTRAL_EMOTION:
            emotions.append(emo)
            confidences.append(conf)
        elif raw_scores:
            best = max(raw_scores, key=raw_scores.get)
            emotions.append(best)
            confidences.append(raw_scores[best])
        else:
            emotions.append(NEUTRAL_EMOTION)
            confidences.append(conf)


    # Stability filter - Remove isolated neutral noise
    trajectory = []
    for emo in emotions:
        if not trajectory or emo != trajectory[-1]:
            trajectory.append(emo)


    # Remove isolated neutral noise for longer trajectories
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


    # ---------------------------------
    # 🔥 UPDATED STEP 2: NARRATIVE-WEIGHTED DOMINANCE
    # ---------------------------------
    emotion_counts = Counter(trajectory)


    # Remove neutral unless it is the only emotion
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


        # frequency + confidence (balanced)
        base = (0.35 * freq) + (0.35 * avg_conf)


        # psychological intensity
        arousal_weight = meta["arousal"] * 0.4
        threat_weight = meta["threat"] * 0.6


        # 🔥 NARRATIVE POSITION WEIGHTING (NEW)
        position_weight = sum(
            (1 - (i / len(emotions))) for i in indices
        ) * 0.25


        emotion_strength[emo] = base + arousal_weight + threat_weight + position_weight


    # ---------------------------------
    # 🔥 UPDATED STEP 3: VALENCE-AWARE SCALING (NO HARD OVERRIDES)
    # ---------------------------------
    for emo in emotion_strength:
        meta = EMOTION_META.get(emo, {})
        if meta.get("valence") == -1:
            emotion_strength[emo] *= 1.15  # Negative emotions get competitive boost
        elif meta.get("valence") == 1:
            emotion_strength[emo] *= 0.95  # Positive emotions slightly discounted


    # ---------------------------------
    # NEW: Normalize emotion strengths into probabilities
    # ---------------------------------
    if emotion_strength:
        total_strength = sum(emotion_strength.values())

        emotion_distribution = {
            emo: round((score / total_strength), 4)
            for emo, score in emotion_strength.items()
        }

        # sort highest → lowest
        emotion_distribution = dict(
            sorted(emotion_distribution.items(), key=lambda x: x[1], reverse=True)
        )
    else:
        emotion_distribution = {}


    # 🔥 STEP 5: SIMPLE FINAL SELECTION (STABLE)
    if not emotion_strength:
        dominant = NEUTRAL_EMOTION
    else:
        dominant = max(emotion_strength.items(), key=lambda x: x[1])[0]


    # 🔥 STEP 6: MAX CONFIDENCE (CORRECTED)
    overall_conf = max(confidences) if confidences else 0.1


    return {
        "overall_emotion": dominant,
        "overall_confidence": round(float(overall_conf), 3),
        "emotion_distribution": emotion_distribution,
        "trajectory": trajectory,
        "trajectory_description": verbalize_emotion_trajectory(trajectory),
        "shift_intensity": shift_intensity,
    }
