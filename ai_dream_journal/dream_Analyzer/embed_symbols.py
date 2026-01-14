import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

from symbol_definitions import SYMBOL_DEFINITIONS

# ---- PATHS ----
BASE_DIR = Path(__file__).resolve().parent.parent
SYMBOL_EMB_PATH = BASE_DIR / "datasets" / "symbol_embeddings.npy"
SYMBOL_META_PATH = BASE_DIR / "datasets" / "symbol_metadata.json"

# ---- MODEL ----
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---- PREPARE SYMBOL TEXTS ----
symbol_names = list(SYMBOL_DEFINITIONS.keys())
symbol_texts = [SYMBOL_DEFINITIONS[s] for s in symbol_names]

# ---- EMBED ----
symbol_embeddings = model.encode(
    symbol_texts,
    normalize_embeddings=True,
    convert_to_numpy=True
)

# ---- SAVE ----
np.save(SYMBOL_EMB_PATH, symbol_embeddings)

with open(SYMBOL_META_PATH, "w", encoding="utf-8") as f:
    json.dump(symbol_names, f, indent=2)

print("Saved symbol embeddings:", symbol_embeddings.shape)
