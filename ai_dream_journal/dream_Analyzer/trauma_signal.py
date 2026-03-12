# trauma_signal.py

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

# ------------------------------
# 1. Emotional Intensity Signal
# ------------------------------
EMOTION_WEIGHTS = {
    "fear": 1.0,
    "anger": 0.8,
    "sadness": 0.25,  # FIXED: Reduced from 0.6
    "shame": 0.9,
    "disgust": 0.7,

    "anticipation": 0.2,
    "surprise": 0.1,
    "trust": -0.4,

    "calm": -0.6,
    "joy": -0.8
}

def emotional_signal(emotion_scores: dict) -> float:
    """Requires net threat dominance. Sadness de-emphasized."""
    raw = sum(
        EMOTION_WEIGHTS.get(e, 0) * p
        for e, p in emotion_scores.items()
    )
    
    # FIXED Problem 3: No positive emotional signal for trauma
    if raw < 0:
        return 0.0
    
    return clamp(raw)

# ------------------------------
# 2. Loss-of-Agency Signal
# ------------------------------
AGENCY_WEIGHTS = {

    # pursuit / threat
    "pursuit": 1.0,
    "attack": 0.9,
    "capture": 1.0,
    "cornered": 0.9,

    # restriction
    "trapped": 1.0,
    "confinement": 1.0,
    "restraint": 1.0,
    "locked": 0.8,
    "blocked": 0.8,
    "barrier": 0.8,
    "stuck": 0.8,

    # instability
    "exposure": 0.7,
    "pressure": 0.7,
    "obstacle": 0.7,
    "stagnation": 0.6,
    "overwhelm": 0.6,

    # resolution signals (reduce trauma)
    "escape": -0.7,
    "relief": -0.6,
    "resolution": -0.8
}

def agency_signal(dynamics: list) -> float:
    raw = sum(AGENCY_WEIGHTS.get(d, 0) for d in dynamics)
    return clamp(raw)

# ------------------------------
# 3. Threat Persistence Signal (UPDATED)
# ------------------------------
def persistence_signal(
    no_resolution: bool,
    repeated_threats: bool,
    emotion_variance: float
) -> float:
    """Low variance only contributes with repeated threats."""
    score = 0.0

    if no_resolution:
        score += 0.4

    if repeated_threats:
        score += 0.3

    # FIXED: Only reward low variance if threat exists
    if emotion_variance < 0.15 and repeated_threats:
        score += 0.2

    return clamp(score)

# ------------------------------
# 4. Recurrence Signal (optional)
# ------------------------------
def recurrence_signal(recurring_count: int) -> float:
    return clamp(recurring_count / 3)

# ------------------------------
# 5. Dream Category Test Suite (STEP 5)
# ------------------------------
TEST_SUITES = {
    "calm_reflective": {
        "emotion_scores": {"calm": 0.8, "joy": 0.1},
        "dynamics": ["resolution"],
        "no_resolution": False,
        "repeated_threats": False,
        "emotion_variance": 0.3,
        "recurring_count": 0,
        "expected": (0, 10),
        "level": "Low"
    },
    "sad_grief": {
        "emotion_scores": {"sadness": 0.7, "calm": 0.2},
        "dynamics": ["stagnation"],
        "no_resolution": True,
        "repeated_threats": False,
        "emotion_variance": 0.2,
        "recurring_count": 0,
        "expected": (5, 15),
        "level": "Low"
    },
    "chase_nightmare": {
        "emotion_scores": {"fear": 0.9},
        "dynamics": ["pursuit", "trapped"],
        "no_resolution": True,
        "repeated_threats": True,
        "emotion_variance": 0.1,
        "recurring_count": 0,
        "expected": (60, 85),
        "level": "Elevated"
    },
    "repeated_threat": {
        "emotion_scores": {"fear": 0.8, "anger": 0.2},
        "dynamics": ["pursuit"],
        "no_resolution": True,
        "repeated_threats": True,
        "emotion_variance": 0.05,
        "recurring_count": 3,
        "expected": (70, 100),
        "level": "High"
    },
    "joyful": {
        "emotion_scores": {"joy": 0.9, "calm": 0.1},
        "dynamics": ["resolution"],
        "no_resolution": False,
        "repeated_threats": False,
        "emotion_variance": 0.4,
        "recurring_count": 0,
        "expected": (0, 0),
        "level": "Low"
    },
    "neutral_random": {
        "emotion_scores": {"neutral": 0.6, "surprise": 0.3},
        "dynamics": [],
        "no_resolution": False,
        "repeated_threats": False,
        "emotion_variance": 0.25,
        "recurring_count": 0,
        "expected": (0, 5),
        "level": "Low"
    }
}

# ------------------------------
# FINAL SCORE with Safeguards
# ------------------------------
def trauma_linked_score(
    emotion_scores: dict,
    dynamics: list,
    no_resolution: bool,
    repeated_threats: bool,
    emotion_variance: float,
    recurring_count: int = 0
) -> tuple[int, str]:
    """
    Returns (score, level) tuple with all safeguards applied.
    """
    # STEP 4 Problem 4: Normalize ONCE at top level for consistency
    total = sum(emotion_scores.values())
    if total > 0:
        emotion_scores = {k: v / total for k, v in emotion_scores.items()}

    # STEP 7: Protect against empty or weak emotion data
    if not emotion_scores:
        return 0, "Low"

    if max(emotion_scores.values()) < 0.2:
        return 0, "Low"
    
    E = emotional_signal(emotion_scores)
    A = agency_signal(dynamics)
    P = persistence_signal(no_resolution, repeated_threats, emotion_variance)
    R = recurrence_signal(recurring_count)

    # ✅ STEP 1: FIXED - Lower thresholds + require threat signal
    # Require at least one meaningful threat signal
    if E < 0.15 and A < 0.15 and not repeated_threats:
        return 0, "Low"

    # STEP 3: Resolution Override (now uses normalized scores)
    if not no_resolution and emotion_scores.get("calm", 0) > 0.3:
        return 0, "Low"

    # ✅ STEP 2: FIXED - Emotion-weighted scoring (E now 45%)
    score = (
        0.45 * E +
        0.25 * A +
        0.20 * P +
        0.10 * R
    )

    # STEP 4: Dream-Type Stabilizer
    positive_strength = (
        emotion_scores.get("calm", 0) +
        emotion_scores.get("joy", 0) +
        emotion_scores.get("trust", 0)
    )
    if positive_strength > 0.5:
        score = score * 0.40

    # STEP 9: Require two signals
    active_signals = sum([E > 0.25, A > 0.25, P > 0.25])
    if active_signals < 2:
        score = score * 0.30

    # STEP 6: Score Bands
    final_score = int(clamp(score) * 100)
    if final_score < 15:
        level = "Low"
    elif final_score < 40:
        level = "Moderate"
    elif final_score < 70:
        level = "High"
    else:
        level = "Very High"

    # STEP 8: Debug logging
    print(f"DEBUG TRAUMA: E:{E:.2f} A:{A:.2f} P:{P:.2f} R:{R:.2f} -> {final_score} ({level})")

    return final_score, level

# Test function
def run_trauma_tests():
    """Run test suite to validate trauma scoring."""
    results = {}
    for name, test in TEST_SUITES.items():
        score, level = trauma_linked_score(**test)
        expected_range = test["expected"]
        in_range = expected_range[0] <= score <= expected_range[1]
        results[name] = {
            "score": score,
            "level": level,
            "expected_range": expected_range,
            "in_range": in_range,
            "expected_level": test["level"]
        }
        print(f"TEST {name}: {score} ({level}) {'✅' if in_range else '❌'}")
    
    return results
