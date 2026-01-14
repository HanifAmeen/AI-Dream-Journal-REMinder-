# utils/symbol_index.py
import os, re, joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from typing import Tuple, List, Dict

MODEL_NAME = os.environ.get("SBERT_MODEL", "all-MiniLM-L6-v2")
MODEL = SentenceTransformer(MODEL_NAME)

def load_symbol_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    cols = {c.lower().strip(): c for c in df.columns}
    word_col = cols.get('word', cols.get('symbol', None))
    interp_col = cols.get('interpretation', cols.get('meaning', None))

    if word_col is None:
        raise ValueError("Symbol CSV missing a 'Word' or 'Symbol' column")

    # Normalize meaning
    if interp_col is None:
        df['interp_first'] = ""
    else:
        df['interp_first'] = df[interp_col].fillna("").apply(
            lambda s: re.split(r'(?<=[.!?])\s+', str(s).strip())[0] if s else ""
        )

    df['word_clean'] = df[word_col].astype(str).str.lower().str.strip()
    df['embed_text'] = (df['word_clean'] + " — " + df['interp_first']).fillna(df['word_clean'])
    return df[['word_clean', 'interp_first', 'embed_text']]

def build_symbol_index(df: pd.DataFrame, persist_dir="models/symbol_index") -> Tuple[pd.DataFrame, object, object]:
    os.makedirs(persist_dir, exist_ok=True)
    texts = df['embed_text'].tolist()
    embeddings = MODEL.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    nn = NearestNeighbors(n_neighbors=min(50, len(texts)), metric='cosine').fit(embeddings)

    joblib.dump((df, embeddings, nn), os.path.join(persist_dir, "symbol_index.joblib"))
    return df, embeddings, nn

def load_symbol_index(persist_dir="models/symbol_index"):
    path = os.path.join(persist_dir, "symbol_index.joblib")
    if not os.path.exists(path):
        raise FileNotFoundError("No symbol index found. Run build_symbol_index first.")
    df, embeddings, nn = joblib.load(path)
    return df, embeddings, nn

def ensure_index(csv_path, persist_dir="models/symbol_index"):
    try:
        return load_symbol_index(persist_dir)
    except FileNotFoundError:
        df = load_symbol_csv(csv_path)
        return build_symbol_index(df, persist_dir)

# ------------------------------------------------------------
# NEW: unified semantic + contextual symbol lookup
# ------------------------------------------------------------
def query_symbols(
    text: str,
    df: pd.DataFrame,
    embeddings,
    nn,
    top_k=12,
    threshold=0.55
) -> List[Dict[str, any]]:
    """
    Returns list of:
        {
            "symbol": string,
            "meaning": string,
            "semantic_score": float
        }
    """

    if df is None or nn is None or not text:
        return []

    try:
        emb = MODEL.encode(text.lower(), convert_to_numpy=True)
        n_neighbors = min(top_k, len(embeddings))
        distances, idxs = nn.kneighbors([emb], n_neighbors=n_neighbors, return_distance=True)
    except Exception:
        return []

    out = []
    for dist, idx in zip(distances[0], idxs[0]):
        score = 1 - float(dist)
        if score < threshold:
            continue

        row = df.iloc[idx]
        out.append({
            "symbol": row["word_clean"],
            "meaning": row["interp_first"],
            "semantic_score": score
        })

    return out
