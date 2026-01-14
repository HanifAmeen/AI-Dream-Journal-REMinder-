# ------------------------------
# Imports
# ------------------------------
import sys
from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# ------------------------------
# Add project root to Python path
# ------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from trauma_signal import trauma_linked_score
from symbol_insight import build_symbol_insight
from resolve_dynamics import resolve_symbol_emotion_dynamics
from interpretation_generator import generate_interpretation

# 🔑 UPDATED import (matches new emotion_detector)
from emotion_detector import (
    detect_emotion_with_scores,
    detect_emotion_trajectory
)

from confidence_utils import (
    compute_symbol_confidence,
    compute_overall_confidence
)

# ------------------------------
# Paths
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SYMBOL_EMB_PATH = BASE_DIR / "datasets" / "symbol_embeddings.npy"
SYMBOL_META_PATH = BASE_DIR / "datasets" / "symbol_metadata.json"

# ------------------------------
# Load symbol data
# ------------------------------
symbol_embeddings = np.load(SYMBOL_EMB_PATH)

with open(SYMBOL_META_PATH, "r", encoding="utf-8") as f:
    symbol_names = json.load(f)

# ------------------------------
# Load SBERT model
# ------------------------------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ------------------------------
# Test dream
# ------------------------------
dream_text = (
    "I was walking alone through a narrow street at night and felt uneasy, as if something might happen. Suddenly, I noticed people watching me from a distance, which made me feel exposed and embarrassed. After a while, I reached a quiet place where I felt safe and calm, and I just stood there breathing slowly"
   
)

# ------------------------------
# Emotion detection (single + trajectory)
# ------------------------------
dominant_emotion, emotion_scores, emotion_confidence = detect_emotion_with_scores(
    dream_text
)

trajectory_result = detect_emotion_trajectory(dream_text)

emotion_trajectory = trajectory_result["trajectory"]
trajectory_description = trajectory_result["trajectory_description"]
trajectory_intensity = trajectory_result["shift_intensity"]

# ------------------------------
# Embed dream + compute similarity
# ------------------------------
dream_embedding = model.encode(dream_text, normalize_embeddings=True)
scores = symbol_embeddings @ dream_embedding

# ------------------------------
# Rank symbols
# ------------------------------
ranked = sorted(
    zip(symbol_names, scores),
    key=lambda x: x[1],
    reverse=True
)

# ------------------------------
# Select top-N symbols
# ------------------------------
TOP_N = 5

raw_symbol_scores = {
    symbol: float(score)
    for symbol, score in ranked[:TOP_N]
}

# ------------------------------
# Symbol insight (grounding)
# ------------------------------
insight = build_symbol_insight(
    raw_symbol_scores,
    dominant_emotion,
    dream_text
)

adjusted_symbol_scores = insight.get("symbol_scores", {})

symbol_confidence = compute_symbol_confidence(adjusted_symbol_scores)

overall_confidence = compute_overall_confidence(
    symbol_confidence,
    emotion_confidence
)

# ------------------------------
# Resolve dynamics
# ------------------------------
dynamics = resolve_symbol_emotion_dynamics(insight, dream_text)

dynamic_names = [
    d["dynamic"]
    for d in dynamics
    if isinstance(d, dict) and "dynamic" in d
]

# ------------------------------
# Generate interpretation
# ------------------------------
interpretation = generate_interpretation(
    dynamics=dynamics,
    dream_text=dream_text,
    dominant_emotion=dominant_emotion
)

# ------------------------------
# Trauma-linked signal computation
# ------------------------------
no_resolution = not any(
    d in {"escape", "relief", "resolution"}
    for d in dynamic_names
)

THREAT_DYNAMICS = {"threat", "harm", "violation", "pressure"}

repeated_threats = sum(
    1 for d in dynamic_names if d in THREAT_DYNAMICS
) >= 2

emotion_variance = (
    float(np.var(list(emotion_scores.values())))
    if emotion_scores else 0.0
)

trauma_score = trauma_linked_score(
    emotion_scores=emotion_scores,
    dynamics=dynamic_names,
    no_resolution=no_resolution,
    repeated_threats=repeated_threats,
    emotion_variance=emotion_variance,
    recurring_count=0
)

# ------------------------------
# Output
# ------------------------------
print("\n--- Emotion Analysis ---")
print("Dominant emotion:", dominant_emotion)
print("Emotion confidence:", round(emotion_confidence, 3))

print("\nEmotion trajectory:", emotion_trajectory)
print("Trajectory description:", trajectory_description)
print("Trajectory intensity:", trajectory_intensity)

print("\n--- Top Symbol Candidates (Raw) ---")
for s, v in raw_symbol_scores.items():
    print(f"{s:15s} → {v:.3f}")

print("\n--- Grounded Symbols (After Insight Filtering) ---")
if adjusted_symbol_scores:
    for s, v in adjusted_symbol_scores.items():
        print(f"{s:15s} → {v:.3f}")
else:
    print("(no symbols passed grounding)")


print("\n--- Dream Text ---\n")
print(dream_text)

print("\n--- Interpretation ---\n")
print(interpretation)

print("\n--- Confidence Scores ---")
print(f"Symbol confidence:  {symbol_confidence:.3f}")
print(f"Emotion confidence: {emotion_confidence:.3f}")
print(f"Overall confidence: {overall_confidence:.3f}")

# ------------------------------
# Trauma assessment output
# ------------------------------
print("\nTrauma-linked signal score:", trauma_score)

if trauma_score < 26:
    label = "Low trauma-linked signals"
elif trauma_score < 51:
    label = "Mild trauma-linked signals"
elif trauma_score < 76:
    label = "Moderate trauma-linked signals"
else:
    label = "Strong trauma-linked signals"

print("Assessment:", label)
