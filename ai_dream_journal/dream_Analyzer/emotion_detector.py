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
# Constants
# ------------------------------
NEUTRAL_EMOTION = "neutral"
SHORT_TEXT_PENALTY = 0.6

EXPLICIT_EMOTION_WORDS = {
    "joy": {"happy", "joy", "excited", "pleased", "delighted", "content"},
    "sadness": {"sad", "cry", "lonely", "grief", "depressed"},
    "fear": {"scared", "afraid", "terrified", "fear", "panic"},
    "anger": {"angry", "furious", "rage", "mad"},
    "calm": {"calm", "peaceful", "relaxed", "serene"},

    # NEW
    "disgust": {"disgusted", "gross", "dirty", "nasty", "rotten"},
    "surprise": {"surprised", "shocked", "suddenly", "unexpected"},
    "trust": {"trusted", "safe", "protected", "secure"},
    "anticipation": {"waiting", "expecting", "anticipate", "hoping"},
    "shame": {"ashamed", "embarrassed", "humiliated", "exposed"}
}


NEGATION_WORDS = {"not", "never", "no", "without", "hardly", "barely"}
CONTRAST_WORDS = {"but", "rather", "instead", "though", "although", "however"}
FEAR_WORDS = {"afraid", "scared", "fearful", "terrified", "anxious", "panic"}
POSITIVE_STATE_WORDS = {"safe", "calm", "peaceful", "relaxed", "secure", "curious"}
INTENSIFIERS = {"very", "extremely", "really", "so", "too", "quite", "deeply"}

WINDOW = 4

EMOTION_ACCEPT_THRESHOLD = 0.35
IMPLICIT_MAX_CONF = 0.55
EXPLICIT_MAX_CONF = 0.75


# ------------------------------
# Core emotion detection
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

    # Explicit emotion detection
    for emotion, words in EXPLICIT_EMOTION_WORDS.items():
        matched = tokens_set & words
        if matched:
            confidence = 0.45 + 0.08 * len(matched)
            for i, token in enumerate(tokens_list):
                if token in matched:
                    left = tokens_list[max(0, i - 2):i]
                    if any(w in INTENSIFIERS for w in left):
                        confidence += 0.08
            return emotion, {}, min(confidence, EXPLICIT_MAX_CONF)

    # Very short dreams
    if word_count < 6:
        return NEUTRAL_EMOTION, {}, 0.15

    # SBERT implicit emotion
    dream_embedding = _model.encode(dream_text, normalize_embeddings=True)
    raw_scores = {
        emotion: float(dream_embedding @ emb)
        for emotion, emb in _EMOTION_EMBEDDINGS.items()
    }

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
# Trajectory verbalizer
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
# Emotion trajectory detection
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

    # Smooth & collapse
    trajectory = []
    for emo in emotions:
        if not trajectory or emo != trajectory[-1]:
            trajectory.append(emo)

    unique_count = len(set(trajectory))
    shift_intensity = (
        "none" if unique_count <= 1 else
        "mild" if unique_count == 2 else
        "moderate" if unique_count == 3 else
        "strong"
    )

    return {
        "overall_emotion": Counter(trajectory).most_common(1)[0][0],
        "overall_confidence": round(float(np.mean(confidences)), 3),
        "trajectory": trajectory,
        "trajectory_description": verbalize_emotion_trajectory(trajectory),
        "shift_intensity": shift_intensity,
    }
