import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer



# ---- PATHS ----
BASE_DIR = Path(__file__).resolve().parent.parent
SYMBOL_EMB_PATH = BASE_DIR / "datasets" / "symbol_embeddings.npy"
SYMBOL_META_PATH = BASE_DIR / "datasets" / "symbol_metadata.json"

# ---- LOAD ----
symbol_embeddings = np.load(SYMBOL_EMB_PATH)

with open(SYMBOL_META_PATH, "r", encoding="utf-8") as f:
    symbol_names = json.load(f)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---- TEST DREAM (semantic text) ----
dream_text = (
    "I was walking with a magic puppy "
   
)



dream_embedding = model.encode(
    dream_text,
    normalize_embeddings=True
)

# ---- COSINE SIMILARITY ----
scores = symbol_embeddings @ dream_embedding

# ---- RANK ----
ranked = sorted(
    zip(symbol_names, scores),
    key=lambda x: x[1],
    reverse=True
)

print("\nSymbol matches:\n")
for symbol, score in ranked:
    print(f"{symbol:15s} → {score:.3f}")
