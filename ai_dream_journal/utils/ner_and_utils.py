# utils/ner_and_utils.py
import re, string
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import numpy as np
import spacy
from typing import List, Dict

# -------------------------------------------------------------
# LAZY-LOADED MODELS
# -------------------------------------------------------------
_summarizer = None
_emotion = None
_kw_model = None
_SBERT = None
_spacy_nlp = None


# -------------------------------------------------------------
# SBERT (shared across analyzer + symbol index)
# -------------------------------------------------------------
def get_sbert():
    global _SBERT
    if _SBERT is None:
        try:
            _SBERT = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _SBERT = None
    return _SBERT


# -------------------------------------------------------------
# SUMMARIZER (robust with fallback)
# -------------------------------------------------------------
def get_summarizer():
    global _summarizer
    if _summarizer is None:
        try:
            _summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception:
            # fallback: lightweight model
            try:
                _summarizer = pipeline("summarization", model="t5-small")
            except Exception:
                _summarizer = None
    return _summarizer


# -------------------------------------------------------------
# EMOTION PIPELINE (robust with fallback)
# -------------------------------------------------------------
def get_emotion_pipeline():
    global _emotion
    if _emotion is None:
        try:
            _emotion = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
        except Exception:
            # fallback model
            try:
                _emotion = pipeline(
                    "text-classification",
                    model="bhadresh-savani/distilbert-base-uncased-emotion",
                    return_all_scores=True
                )
            except Exception:
                _emotion = None
    return _emotion


# -------------------------------------------------------------
# KEYBERT (keyword extraction)
# -------------------------------------------------------------
def get_keybert():
    global _kw_model
    if _kw_model is None:
        try:
            _kw_model = KeyBERT(get_sbert())
        except Exception:
            _kw_model = None
    return _kw_model


# -------------------------------------------------------------
# SPACY (with safe fallback)
# -------------------------------------------------------------
def get_spacy():
    """
    Loads a SpaCy model with full dependency parsing.
    Tries medium model first, then small model.
    If both fail, loads a blank English pipeline.
    """

    # Try medium model (preferred)
    try:
        return spacy.load("en_core_web_md")
    except Exception as e:
        print("[spaCy] Could not load en_core_web_md:", e)

    # Try small model (you installed this one)
    try:
        return spacy.load("en_core_web_sm")
    except Exception as e:
        print("[spaCy] Could not load en_core_web_sm:", e)

    # LAST RESORT — blank model (NO parser!)
    print("[spaCy] WARNING: Using blank 'en' model — noun_chunks will NOT work.")
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp

# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def safe_first_sentence(text: str, max_chars=220) -> str:
    if not text:
        return ""
    t = " ".join(str(text).split())
    m = re.search(r"(.+?[\.!?])\s", t + " ")
    if m:
        return m.group(1).strip()
    if len(t) <= max_chars:
        return t
    part = t[:max_chars]
    return re.sub(r"\s+\S+$", "", part).strip() + "..."


# -------------------------------------------------------------
# CHUNKED SUMMARIZER (stable)
# -------------------------------------------------------------
def chunked_summarize(text: str, max_chunk_words=450):
    summ = get_summarizer()
    if not summ:
        return safe_first_sentence(text, max_chars=200)

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, cur, cur_len = [], [], 0

    for s in sentences:
        cur_len += len(s.split())
        cur.append(s)
        if cur_len >= max_chunk_words:
            chunks.append(" ".join(cur))
            cur, cur_len = [], 0
    if cur:
        chunks.append(" ".join(cur))

    if not chunks:
        return safe_first_sentence(text, max_chars=200)

    summaries = []
    for c in chunks:
        try:
            out = summ(c, max_length=80, min_length=15, do_sample=False)
            summaries.append(out[0]["summary_text"])
        except Exception:
            summaries.append(safe_first_sentence(c, max_chars=180))

    if len(summaries) == 1:
        return summaries[0]

    # summarise combined output
    try:
        combined = " ".join(summaries)
        final = summ(combined, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]
        return final
    except Exception:
        joined = " ".join(summaries)
        return joined[:350] + ("..." if len(joined) > 350 else "")


# -------------------------------------------------------------
# EMOTION DETECTION
# -------------------------------------------------------------
def detect_emotion_text(text: str):
    pipe = get_emotion_pipeline()
    if not pipe:
        return {"dominant": "neutral", "scores": []}

    try:
        res = pipe(text)[0]
        top = max(res, key=lambda x: x.get("score", 0))
        return {"dominant": top["label"], "scores": res}
    except Exception:
        return {"dominant": "neutral", "scores": []}


# -------------------------------------------------------------
# KEYWORD EXTRACTION
# -------------------------------------------------------------
def extract_keywords(text: str, top_n=6):
    kw = get_keybert()
    if not kw:
        words = re.findall(r"\b[a-z]{4,}\b", str(text).lower())
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:top_n]]

    try:
        kws = kw.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            top_n=top_n,
            use_mmr=True,
            diversity=0.6
        )
        return [k[0] for k in kws]
    except Exception:
        return []


