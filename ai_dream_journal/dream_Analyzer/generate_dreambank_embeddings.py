import csv
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm

from sentence_transformers import SentenceTransformer

# ---- PATH SETUP ----
BASE_DIR = Path(__file__).resolve().parent.parent  # ai_dream_journal/
DATASET_PATH = BASE_DIR / "datasets" / "dreambank_processed_full.csv"
EMBEDDING_PATH = BASE_DIR / "datasets" / "dreambank_embeddings.npy"
METADATA_PATH = BASE_DIR / "datasets" / "dreambank_metadata.json"

# ---- LOAD MODEL ----
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---- LOAD DATA ----
texts = []
metadata = []

with open(DATASET_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        text = row.get("semantic_text", "").strip()
        if not text:
            continue

        texts.append(text)
        metadata.append({
            "number": row.get("number"),
            "emotion": row.get("emotion"),
            "character": row.get("character"),
        })

print(f"Loaded {len(texts)} dreams for embedding")

# ---- GENERATE EMBEDDINGS ----
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

# ---- SAVE RESULTS ----
np.save(EMBEDDING_PATH, embeddings)

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print("Embeddings saved to:", EMBEDDING_PATH)
print("Metadata saved to:", METADATA_PATH)
print("Embedding shape:", embeddings.shape)
