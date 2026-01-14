# utils/dreambank_stats.py
import os
import joblib
import numpy as np
import pandas as pd

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

VECT_PATH = os.path.join(ARTIFACT_DIR, "db_vectorizer.joblib")
COOCC_PATH = os.path.join(ARTIFACT_DIR, "db_cooccurrence.joblib")
FREQ_PATH = os.path.join(ARTIFACT_DIR, "db_symbol_freq.joblib")
FEATURES_PATH = os.path.join(ARTIFACT_DIR, "db_features.joblib")
LDA_PATH = os.path.join(ARTIFACT_DIR, "db_lda_model.joblib")

# ------------------------------------------------------------
# BUILDERS
# ------------------------------------------------------------
def build_symbol_stats(reports, min_df=5, ngram_range=(1,2), max_features=5000):
    from sklearn.feature_extraction.text import CountVectorizer

    vect = CountVectorizer(
        stop_words="english",
        ngram_range=ngram_range,
        min_df=min_df,
        max_features=max_features
    )
    X = vect.fit_transform(reports)
    features = vect.get_feature_names_out().tolist()

    freqs = np.array(X.sum(axis=0)).ravel()
    symbol_freq = dict(zip(features, freqs))

    cooc = (X.T @ X).toarray()
    np.fill_diagonal(cooc, 0)

    # Save raw artifacts
    joblib.dump(vect, VECT_PATH)
    joblib.dump(cooc, COOCC_PATH)
    joblib.dump(symbol_freq, FREQ_PATH)
    joblib.dump(features, FEATURES_PATH)

    return {
        "vectorizer": vect,
        "freq": symbol_freq,
        "cooc_mat": cooc,
        "features": features
    }

def build_lda_topics(reports, vectorizer=None, n_topics=12, max_iter=10):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    if vectorizer is None:
        vectorizer = CountVectorizer(stop_words="english", min_df=3, max_features=5000)

    X = vectorizer.fit_transform(reports)
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=max_iter,
        random_state=42
    )
    lda.fit(X)

    joblib.dump(lda, LDA_PATH)
    joblib.dump(vectorizer, VECT_PATH)

    return {"lda": lda, "vectorizer": vectorizer}

def save_all_stats_from_dreambank(df, min_df=5, ngram_range=(1,2), n_topics=12):
    reports = df["report_clean"].tolist()

    stats = build_symbol_stats(reports, min_df=min_df, ngram_range=ngram_range)
    lda_res = build_lda_topics(reports, vectorizer=stats["vectorizer"], n_topics=n_topics)

    return {"symbol_stats": stats, "lda": lda_res}

# ------------------------------------------------------------
# LOADER (returns dict structure needed by analyzer)
# ------------------------------------------------------------
def load_artifacts():
    out = {}

    if not os.path.exists(FREQ_PATH):
        return None  # analyzer handles reduced-context mode

    try:
        freq = joblib.load(FREQ_PATH)
        features = joblib.load(FEATURES_PATH)
        cooc = joblib.load(COOCC_PATH) if os.path.exists(COOCC_PATH) else None
        lda = joblib.load(LDA_PATH) if os.path.exists(LDA_PATH) else None
        vectorizer = joblib.load(VECT_PATH)

        # Convert co-occurrence matrix (N x N) → dict-of-dicts
        cooc_dict = {}
        if cooc is not None:
            for i, term in enumerate(features):
                row = cooc[i]
                cooc_dict[term] = {
                    features[j]: int(row[j]) for j in range(len(features)) if row[j] > 0
                }

        # Build topic labels
        topics = []
        if lda is not None:
            comps = lda.components_
            n_top = 10
            for idx, comp in enumerate(comps):
                top_words = [features[i] for i in comp.argsort()[-n_top:][::-1]]
                topics.append({"topic": idx+1, "top_words": top_words})

        return {
            "freq": freq,
            "cooc": cooc_dict,
            "topics": topics,
            "vectorizer": vectorizer
        }

    except Exception as e:
        print("[DreamBank] load_artifacts failed:", e)
        return None
