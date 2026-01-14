import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# ---- PATHS ----
BASE_DIR = Path(__file__).resolve().parent.parent
EMBEDDINGS_PATH = BASE_DIR / "datasets" / "dreambank_embeddings.npy"
METADATA_PATH = BASE_DIR / "datasets" / "dreambank_metadata.json"

# ---- LOAD ----
embeddings = np.load(EMBEDDINGS_PATH)
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---- TEST DREAM (YOU CAN CHANGE THIS) ----
test_dream = (
    "I was running through a dark place while someone chased me. "
    "I felt scared and could not escape."
)

# ---- EMBED TEST DREAM ----
query_vec = model.encode(
    test_dream,
    normalize_embeddings=True
)

# ---- COSINE SIMILARITY ----
scores = embeddings @ query_vec
top_k = 5
top_indices = np.argsort(scores)[-top_k:][::-1]

print("\nTop similar DreamBank dreams:\n")

for idx in top_indices:
    print(f"Similarity: {scores[idx]:.3f}")
    print(f"Number: {metadata[idx]['number']}")
    print(f"Emotion: {metadata[idx]['emotion']}")
    print(f"Character: {metadata[idx]['character']}")
    print("-" * 50)
