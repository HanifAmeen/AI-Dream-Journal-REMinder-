# trauma_signal.py

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


# ------------------------------
# 1. Emotional Intensity Signal
# ------------------------------
EMOTION_WEIGHTS = {
    "fear": 1.0,
    "anger": 0.8,
    "sadness": 0.6,
    "shame": 0.9,
    "disgust": 0.7,

    "anticipation": 0.2,
    "surprise": 0.1,
    "trust": -0.4,

    "calm": -0.6,
    "joy": -0.8
}



def emotional_signal(emotion_scores: dict) -> float:
    raw = sum(
        EMOTION_WEIGHTS.get(e, 0) * p
        for e, p in emotion_scores.items()
    )
    return clamp(raw)


# ------------------------------
# 2. Loss-of-Agency Signal
# ------------------------------
AGENCY_WEIGHTS = {
    "pursuit": 1.0,
    "trapped": 1.0,
    "barrier": 0.8,
    "exposure": 0.7,
    "stagnation": 0.6,
    "escape": -0.7,
    "relief": -0.6,
    "resolution": -0.8
}


def agency_signal(dynamics: list) -> float:
    raw = sum(AGENCY_WEIGHTS.get(d, 0) for d in dynamics)
    return clamp(raw)


# ------------------------------
# 3. Threat Persistence Signal
# ------------------------------
def persistence_signal(
    no_resolution: bool,
    repeated_threats: bool,
    emotion_variance: float
) -> float:
    score = 0.0

    if no_resolution:
        score += 0.4
    if repeated_threats:
        score += 0.3
    if emotion_variance < 0.15:
        score += 0.3

    return clamp(score)


# ------------------------------
# 4. Recurrence Signal (optional)
# ------------------------------
def recurrence_signal(recurring_count: int) -> float:
    return clamp(recurring_count / 3)


# ------------------------------
# FINAL SCORE
# ------------------------------
def trauma_linked_score(
    emotion_scores: dict,
    dynamics: list,
    no_resolution: bool,
    repeated_threats: bool,
    emotion_variance: float,
    recurring_count: int = 0
) -> int:
    E = emotional_signal(emotion_scores)
    A = agency_signal(dynamics)
    P = persistence_signal(no_resolution, repeated_threats, emotion_variance)
    R = recurrence_signal(recurring_count)

    score = (
        0.35 * E +
        0.30 * A +
        0.20 * P +
        0.15 * R
    )

    return int(clamp(score) * 100)
