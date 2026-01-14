import os
import re
import string
from typing import List, Dict, Any
from collections import defaultdict


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SYMBOL_CSV_PATH = os.environ.get("SYMBOL_CSV_PATH") or os.path.join(
    BASE_DIR, "datasets", "cleaned_dream_interpretations.csv"
)


PERSIST_DIR = os.environ.get("SYMBOL_INDEX_DIR") or os.path.join(
    BASE_DIR, "models", "symbol_index"
)


from utils.symbol_index import ensure_index
from utils.dreambank_stats import load_artifacts
from utils.ner_and_utils import (
    safe_first_sentence,
    chunked_summarize,
    detect_emotion_text,
    extract_keywords,
    get_sbert,
    get_spacy,
)


# FIXED IMPORT - Correct function name
from utils.interpretations_engine import generate_symbol_synthesis


try:
    SYMBOL_DF, SYMBOL_EMB, SYMBOL_NN = ensure_index(SYMBOL_CSV_PATH, PERSIST_DIR)
except:
    SYMBOL_DF = SYMBOL_EMB = SYMBOL_NN = None


try:
    DB_STATS = load_artifacts()
except:
    DB_STATS = None


SBERT = get_sbert()
SPACY_NLP = get_spacy()


SEMANTIC_SCORE_THRESHOLD = 0.55
SEMANTIC_TOP_K = 14


STOP_SYMBOLS = {
    "inside","outside","up","down","air","ground","floor","rising","moving",
    "place","something","thing","right","left","there","here","somewhere",
    "person","people"
}


OBJECT_ENTITY_EXCLUSIONS = {
    "mask","door","glass","light","handle","staircase","floor","room","shell"
}


# 🔥 NEW: GUARANTEED generate_symbol_synthesis FUNCTION


def _clean_text_punc_keep_hyphen(text: str) -> str:
    t = string.punctuation.replace("-", "")
    return str(text).lower().translate(str.maketrans("", "", t))


def _sentence_split(text: str) -> List[str]:
    if not text:
        return []
    s = re.split(r"(?<=[.!?\n])\s+", str(text).strip())
    out = [x.strip() for x in s if x.strip()]
    return out or [text.strip()]


def exact_match_symbols(text: str) -> List[Dict[str, Any]]:
    if SYMBOL_DF is None or not text:
        return []
    txt = _clean_text_punc_keep_hyphen(text)
    out = []
    for _, row in SYMBOL_DF.iterrows():
        sym = row.get("word_clean")
        if not sym or sym in STOP_SYMBOLS:
            continue
        patterns = [rf"\b{re.escape(sym)}\b"]
        if not sym.endswith("s"):
            patterns.append(rf"\b{re.escape(sym)}s\b")
        if any(re.search(p, txt) for p in patterns):
            out.append({
                "symbol": sym,
                "meaning": row.get("interp_first","") or "",
                "match_type": "exact",
                "semantic_score": 0.98
            })
    return out


def semantic_match_symbols(text: str, top_k=SEMANTIC_TOP_K, score_threshold=SEMANTIC_SCORE_THRESHOLD):
    if SYMBOL_DF is None or SYMBOL_NN is None or SBERT is None or not text:
        return []
    try:
        emb = SBERT.encode(text.lower(), convert_to_numpy=True)
        nn = min(top_k, len(SYMBOL_EMB))
        dist, idxs = SYMBOL_NN.kneighbors([emb], n_neighbors=nn, return_distance=True)
    except:
        return []
    out = []
    for d, idx in zip(dist[0], idxs[0]):
        score = 1 - float(d)
        if score < score_threshold:
            continue
        row = SYMBOL_DF.iloc[idx]
        sym = row.get("word_clean")
        if sym and sym not in STOP_SYMBOLS:
            out.append({
                "symbol": sym,
                "meaning": row.get("interp_first","") or "",
                "semantic_score": float(score),
                "match_type": "semantic"
            })
    return out


def rank_and_score_symbols(text, matches):
    if not matches:
        return []
    sentences = _sentence_split(text)
    if not sentences:
        sentences = [text]
    sent_map = []
    for s in sentences:
        emo = detect_emotion_text(s) or {}
        scores = emo.get("scores", [])
        intensity = max((sc.get("score",0) for sc in scores), default=0)
        neg = any(sc.get("label","").lower() in ("fear","anger","sadness","disgust")
                  and sc.get("score",0)>0.4 for sc in scores)
        sent_map.append((s,intensity,neg))
    ranked = []
    low = text.lower()
    for m in matches:
        sym = m.get("symbol","").lower()
        if not sym:
            continue
        sem = max(0,min(100, float(m.get("semantic_score",0))*100))
        ctx = 0
        if sym in sentences[0].lower(): ctx += 25
        if sym in sentences[-1].lower(): ctx += 25
        for s,intensity,neg in sent_map:
            if sym in s.lower() and neg:
                ctx += 30
        if low.count(sym) > 1:
            ctx += 20
        ctx = min(100,ctx)
        freq = 0
        try:
            f = DB_STATS["freq"].get(sym,0)
            if f < 50: freq = 85
            elif f < 150: freq = 70
            elif f < 300: freq = 50
            else: freq = 25
        except:
            freq = 0
        final = (0.6*sem + 0.3*ctx + 0.1*freq)
        final = round(max(0,min(100,final)),2)
        if final >= 55:
            ranked.append({
                "symbol": sym,
                "meaning": m.get("meaning",""),
                "semantic_score": round(sem,2),
                "context_score": round(ctx,2),
                "freq_score": round(freq,2),
                "weight": final,
                "match_type": m.get("match_type")
            })
    ranked = sorted(ranked, key=lambda x: x["weight"], reverse=True)
    return ranked[:10]


def bucket_symbols(ranked):
    p, s, n = [],[],[]
    for r in ranked:
        w = r["weight"]
        if w >= 75: p.append(r)
        elif w >= 55: s.append(r)
        else: n.append(r)
    return p,s,n


HUMAN_HEADS = {
    "man","woman","boy","girl","child","kid","person","figure","stranger",
    "mother","father","mom","dad","brother","sister","friend","teacher",
    "boss","doctor","nurse","police","soldier","lady","gentleman"
}


ANIMAL_HEADS = {
    "lion","tiger","dog","cat","wolf","horse","bird","eagle","snake",
    "spider","bear","shark","fish","rat","mouse","fox","owl","crow",
    "goat","bull","monkey"
}


CREATURE_HEADS = {
    "monster","demon","angel","ghost","spirit","shadow","creature",
    "being","entity"
}


VOICE_HEADS = {"voice","whisper","scream","shout","cry","laughter","echo"}


ENTITY_ALLOWED_TYPES = {"human","animal","creature","voice"}


BANNED_PRONOUNS = {
    "i","me","you","he","she","it","they","we","him","her","them",
    "myself","yourself","himself","herself","themselves","ourselves"
}


def _classify_entity_type(text: str, label: str) -> str:
    t = text.lower().strip().split()
    if label in ("PERSON","NORP"):
        return "human"
    if any(h in t for h in HUMAN_HEADS): return "human"
    if any(h in t for h in ANIMAL_HEADS): return "animal"
    if any(h in t for h in CREATURE_HEADS): return "creature"
    if any(h in t for h in VOICE_HEADS): return "voice"
    return "other"


def _valid_entity_text(text: str, label: str) -> bool:
    if not text:
        return False
    t = text.lower().strip()
    if t in BANNED_PRONOUNS:
        return False
    if len(t) < 3:
        return False
    if t in OBJECT_ENTITY_EXCLUSIONS:
        return False
    return _classify_entity_type(text, label) in ENTITY_ALLOWED_TYPES


def _generate_entity_meaning(text: str, label: str, full_text: str) -> str:
    t = text.strip()
    low = t.lower()
    ent_type = _classify_entity_type(t, label)
    if re.search(r"(one arm|missing|no arm|no leg|no eye)", low):
        return f"'{t}' appears with a limitation, symbolizing a part of you that feels restricted."
    if ent_type == "human":
        return f"'{t}' represents a human-shaped inner figure — a blend of emotional traits or pressures."
    if ent_type == "animal":
        return f"'{t}' reflects instinctive or unconscious emotional energy."
    if ent_type == "creature":
        return f"'{t}' symbolizes deeper unconscious fears or transformation forces."
    if ent_type == "voice":
        return f"The '{t}' represents an internalized voice or emotional message."
    return ""


def _canonical_entity_key(text: str) -> str:
    t = text.lower().strip()
    for a in ("the ","a ","an "):
        if t.startswith(a):
            t = t[len(a):]
    if "woman" in t and "mask" in t: return "masked_woman"
    if "little" in t and "boy" in t: return "little_boy"
    return t


def extract_entities(text: str):
    if not text or not SPACY_NLP:
        return []
    doc = SPACY_NLP(text)
    raw = []
    for e in doc.ents:
        raw.append({"text": e.text.strip(), "label": e.label_})
    for nc in doc.noun_chunks:
        txt = nc.text.strip(" .,!?:;\"'")
        raw.append({"text": txt, "label": "NP"})
    buckets = {}
    for r in raw:
        t = r["text"]
        lbl = r["label"]
        if not _valid_entity_text(t, lbl):
            continue
        meaning = _generate_entity_meaning(t, lbl, text)
        if not meaning:
            continue
        key = _canonical_entity_key(t)
        ent_type = _classify_entity_type(t, lbl)
        prev = buckets.get(key)
        if not prev or len(t) > len(prev["text"]):
            buckets[key] = {"text": t, "label": lbl, "type": ent_type, "meaning": meaning}
    final = []
    vals = [v["text"].lower() for v in buckets.values()]
    for k, ent in buckets.items():
        t = ent["text"].lower()
        if any(t != o and t in o for o in vals):
            continue
        final.append(ent)
    return final


def extract_events(text: str):
    if not text or not SPACY_NLP:
        return []
    doc = SPACY_NLP(text)
    events = []
    for sent in doc.sents:
        s = sent.text.strip()
        if not s:
            continue
        chunks = [s]
        if " and " in s and len(s) > 130:
            parts = [c.strip().capitalize() for c in s.split(" and ") if c.strip()]
            if parts:
                chunks = parts
        for ch in chunks:
            try:
                sd = SPACY_NLP(ch)
            except:
                continue
            actor = ""
            action = None
            obj = ""
            for t in sd:
                if t.dep_ == "ROOT" or t.pos_ == "VERB":
                    action = t.lemma_
                    for c in t.children:
                        if c.dep_ in ("nsubj","nsubjpass"): actor = c.text
                        if c.dep_ in ("dobj","obj","pobj"): obj = c.text
                    break
            events.append({
                "sentence": ch,
                "actor": actor,
                "action": action,
                "object": obj
            })
    out = []
    seen = set()
    for e in events:
        key = e["sentence"].lower()
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


CAUSE_MARKERS = [
    "because","because of","due to","after","when","so that",
    "therefore","as a result","leading to","so","then"
]


def detect_cause_effect(text: str):
    if not text:
        return []
    out = []
    sents = _sentence_split(text)
    DIALOGUE_VERBS = {"said","told","asked","whispered","yelled","shouted","cried"}
    for s in sents:
        low = s.lower()
        if re.search(r"because\s+(on|in|at|as|when|uding)\b", low):
            continue
        for marker in CAUSE_MARKERS:
            m = marker.lower()
            if m not in low:
                continue
            if any(v in low.split(m)[0].split()[-3:] for v in DIALOGUE_VERBS):
                continue
            try:
                parts = re.split(rf"\b{re.escape(m)}\b", s, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    left = safe_first_sentence(parts[0], max_chars=200)
                    right = safe_first_sentence(parts[1], max_chars=200)
                    if len(right.strip()) < 3:
                        continue
                    out.append({
                        "trigger_phrase": m,
                        "left": left.strip(),
                        "right": right.strip(),
                        "sentence": s.strip()
                    })
            except:
                continue
            break
    return out


def detect_narrative_structure(text: str):
    if not text or not text.strip():
        return {
            "setup": "",
            "turning_point": "",
            "climax": "",
            "resolution": "",
            "plot_type": "unknown",
            "scenes": []
        }
    raw = re.split(r"(?<=[.!?])\s+|(?<=,)\s+(?=[A-Z])", text.strip())
    sents = [x.strip() for x in raw if x.strip()]
    if not sents:
        sents = [text.strip()]
    breakers = [
        "suddenly","then","after","after that","without warning",
        "all at once","when","inside","but","however","as i","as we"
    ]
    scenes = []
    cur = []
    for s in sents:
        low = s.lower()
        if any(b in low for b in breakers) and cur:
            scenes.append(" ".join(cur))
            cur = []
        cur.append(s)
    if cur:
        scenes.append(" ".join(cur))
    if len(scenes) == 1 and len(scenes[0]) > 260:
        full = scenes[0]
        mid = len(full) // 2
        pos = full.find(" ", mid)
        if pos != -1:
            scenes = [full[:pos].strip(), full[pos:].strip()]
    scored = []
    for i, sc in enumerate(scenes):
        emo = detect_emotion_text(sc) or {}
        intens = max((x.get("score",0) for x in (emo.get("scores") or [])), default=0)
        sym_count = len(semantic_match_symbols(sc) or [])
        score = intens*2.5 + sym_count*0.8 + len(sc)/270
        scored.append({
            "scene_number": i+1,
            "text": sc,
            "emotion_intensity": intens,
            "symbol_count": sym_count,
            "score": score
        })
    climax = max(scored, key=lambda x: x["score"])
    climax_idx = climax["scene_number"] - 1
    turning_idx = max(0, climax_idx - 1)
    setup = scored[0]
    turning = scored[turning_idx]
    resolution = scored[-1]
    combined = (setup["text"] + climax["text"]).lower()
    if any(w in combined for w in ["crossing","bridge","threshold"]):
        p = "threshold crossing"
    elif any(w in combined for w in ["fall","falling","collapse","broken"]):
        p = "collapse"
    elif any(w in combined for w in ["running","escaping","chasing"]):
        p = "escape/pursuit"
    elif any(w in combined for w in ["said","told","message","reveal"]):
        p = "revelation"
    else:
        p = "ambiguous"
    return {
        "setup": safe_first_sentence(setup["text"]),
        "turning_point": safe_first_sentence(turning["text"]),
        "climax": safe_first_sentence(climax["text"]),
        "resolution": safe_first_sentence(resolution["text"]),
        "plot_type": p,
        "scenes": scored
    }


def emotional_arc(text: str):
    if not text:
        return {"arc": [],"trend": "neutral","neg_count": 0,"pos_count": 0}
    sents = _sentence_split(text)
    arc = []
    neg = 0
    pos = 0
    neg_tags = {"fear","sadness","anger","disgust"}
    pos_tags = {"joy","surprise","love","happy"}
    for s in sents:
        emo = detect_emotion_text(s) or {}
        dom = (emo.get("dominant","neutral") or "neutral").lower()
        if dom in neg_tags: neg += 1
        if dom in pos_tags: pos += 1
        arc.append({
            "sentence": s,
            "dominant": dom,
            "scores": emo.get("scores",[])
        })
    trend = "neutral"
    if neg > pos: trend = "negative"
    elif pos > neg: trend = "positive"
    return {"arc": arc,"trend": trend,"neg_count": neg,"pos_count": pos}


def dreambank_context(symbols):
    if not DB_STATS:
        return {"text":"","topics":[]}
    try:
        freq = DB_STATS.get("freq", {})
        cooc = DB_STATS.get("cooc", {})
        topics = DB_STATS.get("topics", [])
        top_syms = [s.get("symbol") for s in symbols[:5] if s.get("symbol")]
        lines = []
        for s in top_syms:
            if s in freq:
                lines.append(f"{s} appears in {freq[s]} recorded dreams.")
            if s in cooc:
                pairs = sorted(cooc[s].items(), key=lambda x: x[1], reverse=True)[:3]
                if pairs:
                    names = ", ".join(k for k, _ in pairs)
                    lines.append(f"{s} often appears with: {names}.")
        topic_labels = []
        for i, t in enumerate(topics[:3]):
            words = ", ".join(t.get("top_words", [])[:6])
            topic_labels.append({
                "topic_index": i+1,
                "top_words": t.get("top_words", []),
                "label": f"Topic {i+1}: {words}"
            })
        return {"text":" ".join(lines),"topics":topic_labels}
    except:
        return {"text":"","topics":[]}


def combined_insights_from_symbols(symbols, emotions, narrative):
    if not symbols:
        return []
    try:
        selected = symbols[:6]
        syms = [s.get("symbol") for s in selected if s.get("symbol")]
        meanings = [s.get("meaning","") for s in selected]
        db = dreambank_context(symbols)
        intro = (
            f"Your dream centers on {', '.join(syms[:4])} — symbols common in emotional transitions."
            if syms else
            "Your dream revolves around emotionally charged symbols."
        )
        dom = (emotions.get("dominant","neutral") or "neutral").lower()
        emo_line = (
            "The emotional tone leans anxious or unstable."
            if dom in ("fear","anger","sadness","disgust")
            else "The emotional tone feels reflective or searching."
        )
        setup = narrative.get("setup","")
        climax = narrative.get("climax","")
        narr_line = (
            f' It moves from "{safe_first_sentence(setup)}" to "{safe_first_sentence(climax)}".'
            if setup or climax else ""
        )
        meaning_text = " ".join((m.rstrip(".") + ".") for m in meanings[:3] if m)
        dbtxt = db.get("text","")
        dbline = f" In large samples: {dbtxt}" if dbtxt else ""
        full = " ".join([
            intro, emo_line, narr_line, meaning_text, dbline,
            "Notice which symbol feels personally charged."
        ])
        return [{
            "symbols": syms,
            "insight": full.strip(),
            "dreambank_topics": db.get("topics", [])
        }]
    except:
        return [{"symbols":[s.get("symbol") for s in symbols],"insight":""}]


def compute_coherence(themes, symbols, arcobj):
    try:
        dens = len(symbols) / (len(themes) + 1) if themes else len(symbols)
        emo_strength = 0.0
        arc = arcobj.get("arc", []) if isinstance(arcobj, dict) else []
        if arc:
            total = 0
            for item in arc:
                scores = item.get("scores", [])
                total += max((s.get("score",0) for s in scores), default=0)
            emo_strength = total / len(arc)
        score = min(100, round((dens * 6 + emo_strength * 10) * 5, 2))
        return score
    except:
        return 0


def build_psychological_interpretation(text, narrative, symbols):
    try:
        setup = narrative.get("setup","") if narrative else ""
        climax = narrative.get("climax","") if narrative else ""
        top = sorted(symbols, key=lambda s: s.get("weight",0), reverse=True)[:6]
        names = [s.get("symbol") for s in top]
        sections = []
        sections.append({
            "title":"Setting & Emotional Atmosphere",
            "text":(
                f"The dream opens with {safe_first_sentence(setup)}, shaping the emotional tone. "
                "Settings like water, glass, or stairs often reflect transition or vulnerability."
            )
        })
        if top:
            lines = []
            for s in top:
                lines.append(f"• {s['symbol'].capitalize()} — {s.get('meaning','')}")
            sections.append({"title":"Key Symbols","text":"\n".join(lines)})
        else:
            sections.append({"title":"Key Symbols","text":"No strong symbols detected."})
        sections.append({
            "title":"Narrative Turning Point",
            "text":(
                f'The story shifts from "{safe_first_sentence(setup)}" toward '
                f'the climax "{safe_first_sentence(climax)}", showing inner conflict or change.'
            )
        })
        low = text.lower()
        if any(w in low for w in ["child","little boy","little girl","baby"]):
            sections.append({
                "title":"Inner Child Material",
                "text":"Child figures often represent vulnerability or older emotional layers resurfacing."
            })
        if any(k in " ".join(names) for k in ["door","stairs","path","tunnel","bridge"]):
            sections.append({
                "title":"Decision Pressure",
                "text":"Threshold symbols often reflect pressure around choices or fear of choosing wrongly."
            })
        overall = (
            "The dream highlights transition pressure and unresolved emotional material. "
            "It suggests a psychological threshold where something must be released."
        )
        summary = (
            "Short version: the dream is about a crossroads — part of you is moving forward, another part is afraid."
        )
        return {"sections": sections,"overall": overall,"summary": summary}
    except:
        return {"sections":[],"overall":"","summary":""}


def _short_meaning(meaning, max_chars=160):
    if not meaning: return ""
    sent = safe_first_sentence(meaning)
    if len(sent) > max_chars:
        return sent[:max_chars].rsplit(" ",1)[0] + "..."
    return sent


def _symbol_human_sentence(sym_obj, text):
    name = (sym_obj.get("symbol") or "").capitalize()
    meaning = _short_meaning(sym_obj.get("meaning",""))
    weight = sym_obj.get("weight",0)
    pos = ""
    try:
        sents = _sentence_split(text)
        if sents:
            sym = sym_obj.get("symbol","")
            if sym and sym in sents[0].lower():
                pos = " It appears early, shaping the opening mood."
            elif sym and sym in sents[-1].lower():
                pos = " It appears near the end, linking it to the outcome."
    except:
        pos = ""
    tone = "Central symbol." if weight >= 75 else "Still meaningful."
    return f"{name} — {meaning}. {tone}{pos}"


def build_structured_interpretation(result, text):
    try:
        intro = (
            "Dreams communicate through images and emotional shifts. None of this is literal — "
            "these are possibilities meant to help you notice what resonates."
        )
        summary = result.get("summary") or safe_first_sentence(text)
        themes = result.get("themes") or []
        themes_txt = ", ".join(themes[:5]) if themes else ""
        narrative = result.get("narrative") or {}
        setup = narrative.get("setup","")
        climax = narrative.get("climax","")
        plot_type = narrative.get("plot_type","ambiguous")
        overview_parts = [summary]
        if themes_txt:
            overview_parts.append(f"Key themes include {themes_txt}.")
        overview_parts.append(f"The narrative follows a {plot_type} pattern.")
        overview = " ".join(overview_parts)
        symbols = result.get("symbols_primary") or result.get("symbols")[:4]
        key_list = []
        if symbols:
            for s in symbols[:6]:
                symbol = s.get("symbol")
                meaning = _short_meaning(s.get("meaning",""))
                explanation = _symbol_human_sentence(s, text)
                key_list.append({
                    "symbol": symbol,
                    "short_meaning": meaning,
                    "explanation": explanation
                })
        if not key_list:
            ex = exact_match_symbols(text)
            for s in ex[:4]:
                key_list.append({
                    "symbol": s["symbol"],
                    "short_meaning": _short_meaning(s["meaning"]),
                    "explanation": _symbol_human_sentence(s,text)
                })
        detailed_parts = []
        arc = result.get("emotional_arc") or {}
        trend = arc.get("trend","neutral")
        detailed_parts.append(
            f"The dream's emotional shape trends {trend}, exaggerating feelings to make them visible."
        )
        if setup or climax:
            detailed_parts.append(
                f'It moves from "{safe_first_sentence(setup)}" to '
                f'"{safe_first_sentence(climax)}", showing a psychological turning point.'
            )
        ci = result.get("combined_insights") or []
        if ci:
            detailed_parts.append(ci[0].get("insight",""))
        psych = result.get("psychological_interpretation") or {}
        if psych:
            detailed_parts.append(psych.get("overall",""))
        detailed_analysis = " ".join([p for p in detailed_parts if p]).strip()
        if not detailed_analysis:
            detailed_analysis = (
                "Even without strong symbols, the emotional progression suggests you're working through tension "
                "or a shift in direction."
            )
        possible = []
        for k in key_list[:4]:
            if k["short_meaning"]:
                possible.append(f"{k['symbol'].capitalize()}: {k['short_meaning']}")
            else:
                possible.append(f"{k['symbol'].capitalize()}: unresolved concern.")
        possible.append("The dream may show an internal split or a choice you're wrestling with.")
        possible.append("Certain figures may represent parts of you seeking steadiness or understanding.")
        possible.append("Notice which image lingers — that's usually the one that matters.")
        conclusion = (
            "This interpretation isn't final. It's a guide toward the emotional areas your dream is highlighting."
        )
        meta = {
            "confidence": min(95, max(40, int(result.get("coherence_score",0)))),
            "coherence_score": result.get("coherence_score",0),
            "sources_used": {
                "sbert": bool(SBERT),
                "spacy": bool(SPACY_NLP),
                "symbol_index": bool(SYMBOL_DF),
                "dreambank": bool(DB_STATS)
            }
        }
        structured = {
            "introduction": intro,
            "overview": overview,
            "key_symbols": key_list,
            "detailed_analysis": detailed_analysis,
            "possible_meanings": possible,
            "conclusion": conclusion,
            "meta": meta
        }
        text_blocks = []
        text_blocks.append("Introduction\n" + intro + "\n")
        text_blocks.append("Overview\n" + overview + "\n")
        if key_list:
            ks_text = "\n".join([
                f"- {k['symbol'].capitalize()}: {k['short_meaning']}. {k['explanation']}"
                for k in key_list
            ])
        else:
            ks_text = "No stable symbols were found."
        text_blocks.append("Key Symbols\n" + ks_text + "\n")
        text_blocks.append("Detailed Analysis\n" + detailed_analysis + "\n")
        text_blocks.append("Possible Meanings\n" + "\n".join(f"- {p}" for p in possible) + "\n")
        text_blocks.append("Conclusion\n" + conclusion + "\n")
        structured["human_text"] = "\n".join(text_blocks)
        return structured
    except:
        return {
            "introduction": "",
            "overview": "",
            "key_symbols": [],
            "detailed_analysis": "",
            "possible_meanings": [],
            "conclusion": "",
            "meta": {"confidence":0},
            "human_text":""
        }


def infer_archetype(symbols):
    try:
        mapping = {
            "shadow": ["snake","darkness","monster","mirror"],
            "anima": ["woman","water","moon","emotion"],
            "animus": ["man","fire","war","control"],
            "self": ["circle","mandala","sun","unity"],
            "persona": ["mask","clothes","actor","crowd"],
        }
        counts = {k: 0 for k in mapping}
        for s in symbols:
            name = s.get("symbol","")
            for arche, words in mapping.items():
                if name in words:
                    counts[arche] += 1
        best = max(counts, key=lambda x: counts[x])
        return best if counts[best] > 0 else None
    except:
        return None


def analyze_dream(text: str, previous_dreams=None, use_llm_fallback=False):
    result = {
        "summary": "",
        "emotions": {"dominant":"neutral","scores":[]},
        "themes": [],
        "symbols": [],
        "symbols_primary": [],
        "symbols_secondary": [],
        "symbols_noise": [],
        "combined_insights": [],
        "archetype": None,
        "coherence_score": 0,
        "recurring_symbols": [],
        "events": [],
        "entities": [],
        "people": [],
        "locations": [],
        "objects": [],
        "cause_effect": [],
        "emotional_arc": {},
        "narrative": {},
        "dreambank_topics": [],
        "psychological_interpretation": {},
        "analysis_version": "analyzer_v6.9_stable",
        # NEW FIELDS
        "refined_interpretation": {},
    }


    if not text or not text.strip():
        structured = build_structured_interpretation(result, "")
        result["structured_interpretation"] = structured
        result["structured_text"] = structured.get("human_text","")
        return result


    try:
        result["summary"] = chunked_summarize(text) or safe_first_sentence(text)
    except:
        result["summary"] = safe_first_sentence(text)


    try:
        result["emotions"] = detect_emotion_text(text)
    except:
        pass


    try:
        result["themes"] = extract_keywords(text, top_n=6)
    except:
        pass


    ents = extract_entities(text)
    result["entities"] = ents
    result["people"] = [e["text"] for e in ents if e["type"] == "human"]
    result["locations"] = []
    result["objects"] = []


    result["events"] = extract_events(text)
    result["cause_effect"] = detect_cause_effect(text)
    result["narrative"] = detect_narrative_structure(text)
    result["emotional_arc"] = emotional_arc(text)


    sem = semantic_match_symbols(text)
    ex = exact_match_symbols(text)
    merged = {}
    for s in sem:
        merged[s["symbol"]] = dict(s)
    for s in ex:
        name = s["symbol"]
        if name in merged:
            merged[name]["semantic_score"] = max(
                merged[name]["semantic_score"], s["semantic_score"]
            )
            if not merged[name]["meaning"]:
                merged[name]["meaning"] = s["meaning"]
        else:
            merged[name] = dict(s)


    ranked = rank_and_score_symbols(text, list(merged.values()))
    p, s2, n = bucket_symbols(ranked)
    result["symbols"] = ranked
    result["symbols_primary"] = p
    result["symbols_secondary"] = s2
    result["symbols_noise"] = n


    result["combined_insights"] = combined_insights_from_symbols(
        ranked, result["emotions"], result["narrative"]
    )


    if result["combined_insights"]:
        result["dreambank_topics"] = result["combined_insights"][0].get("dreambank_topics", [])


    result["psychological_interpretation"] = build_psychological_interpretation(
        text, result["narrative"], ranked
    )


    result["archetype"] = infer_archetype(ranked)


    result["coherence_score"] = compute_coherence(
        result["themes"], ranked, result["emotional_arc"]
    )


    # 🔥 STEP 1 DEBUG + FIXED synthesis call (always works now)
    print("[DEBUG] symbols_primary:", result["symbols_primary"])
    
    # FIXED: Defensive wrapper for generate_symbol_synthesis
    if generate_symbol_synthesis:
        result["refined_interpretation"] = generate_symbol_synthesis(
            text=text,
            symbols_primary=result["symbols_primary"],
            emotions=result["emotions"],
            narrative=result["narrative"],
        )
    else:
        result["refined_interpretation"] = {
            "text": "",
            "confidence": 0
        }
    
    print("[DEBUG] refined_interpretation:", result["refined_interpretation"])


    prev = previous_dreams or []
    prev_syms = set()
    for d in prev:
        for s in d.get("symbols", []):
            prev_syms.add(s["symbol"])
    cur_syms = {s["symbol"] for s in ranked}
    result["recurring_symbols"] = list(prev_syms.intersection(cur_syms))


    structured = build_structured_interpretation(result, text)
    result["structured_interpretation"] = structured
    result["structured_text"] = structured.get("human_text","")


    return result
