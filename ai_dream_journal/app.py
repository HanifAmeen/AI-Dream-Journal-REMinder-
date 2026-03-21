import sys
import os
os.environ["PYTHONLEGACYWINDOWSSTDIO"] = "1"  # ✅ FIX #1: Windows console crash
from pathlib import Path
import re
from collections import Counter
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import uuid  # ✅ MOVED UP - NEEDED FOR BATCHING
import numpy as np  # MOVED UP - NEEDED FOR DREAMBANK
from flask import redirect
from flask_mail import Mail, Message


BASE_DIR = Path(__file__).resolve().parent


ANALYZER_DIR = BASE_DIR / "dream_Analyzer"
VISUALIZER_DIR = BASE_DIR / "dream_visualizer"
CHATBOT_DIR = BASE_DIR / "Chatbot"
sys.path.insert(0, str(CHATBOT_DIR))
sys.path.insert(0, str(ANALYZER_DIR))
sys.path.insert(0, str(VISUALIZER_DIR))


import json
import traceback
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import jwt
import bcrypt
from functools import wraps


# ============================================================
# 🔥 LAZY IMPORT WRAPPERS (prevents startup blocking)
# ============================================================


def get_scene_splitter():
    from ai_dream_journal.dream_Visualizer.scene_splitter import split_into_scenes
    return split_into_scenes


def get_prompt_builder():
    from ai_dream_journal.dream_Visualizer.prompt_builder import build_prompt
    return build_prompt


def get_image_generator():
    from ai_dream_journal.dream_Visualizer.image_generator import generate_image
    return generate_image


def get_chatbot_bp():
    from ai_dream_journal.Chatbot.chatbot_api import chatbot_bp
    return chatbot_bp


def get_sentence_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer
    except:
        print("⚠️ sentence-transformers not installed")
        return None


def get_trauma_signal():
    from ai_dream_journal.dream_Analyzer.trauma_signal import trauma_linked_score
    return trauma_linked_score


def get_symbol_insight():
    from ai_dream_journal.dream_Analyzer.symbol_insight import build_symbol_insight
    return build_symbol_insight


def get_resolve_dynamics():
    from ai_dream_journal.dream_Analyzer.resolve_dynamics import resolve_symbol_emotion_dynamics
    return resolve_symbol_emotion_dynamics


def get_interpretation():
    from ai_dream_journal.dream_Analyzer.interpretation_generator import generate_interpretation
    return generate_interpretation


def get_emotion_detector():
    from ai_dream_journal.dream_Analyzer.emotion_detector import (
        detect_emotion_with_scores,
        detect_emotion_trajectory
    )
    return detect_emotion_with_scores, detect_emotion_trajectory


def get_confidence_utils():
    from ai_dream_journal.dream_Analyzer.confidence_utils import (
        compute_symbol_confidence,
        compute_overall_confidence
    )
    return compute_symbol_confidence, compute_overall_confidence


def get_dream_similarity():
    print("⚠️ DreamSimilarity disabled (manually disabled)")
    return None


# Download NLTK data (one-time)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')


lemmatizer = WordNetLemmatizer()


# -------------------------------------------------
# 🛡️ SAFE SERIALIZATION HELPERS
# -------------------------------------------------
def ensure_string(value):
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def ensure_json(value):
    if isinstance(value, dict):
        return value
    return {}


# -------------------------------------------------
# 🔧 FIX #2 - EXPANDED WEAK SYMBOLS FILTER (100+ entries) ✅ APPLIED
# -------------------------------------------------
WEAK_SYMBOLS = {
    # (intentionally left commented out / empty in your snippet)
}


# -------------------------------------------------
# 📦 AUTOMATIC SYMBOL CLASSIFICATION (SCALABLE ✅)
# -------------------------------------------------
ABSTRACT_SYMBOLS = {
    "pursuit", "avoidance", "searching", "stagnation", "transition",
    "loss_of_control", "powerlessness", "agency", "threat", "protection",
    "vulnerability", "exposure", "confinement", "barrier", "openness",
    "threshold", "pressure", "tension", "relief", "separation", "connection",
    "conflict", "observation", "instability", "order", "disruption",
    "role_shift", "evaluation"
}


RESOLUTION_PHRASES = {
    'escaped', 'safe', 'relieved', 'clear', 'outside', 'calm',
    'woke up', 'found way', 'finally', 'peace', 'home'
}


# -------------------------------------------------
# 🧬 LIVING ENTITY DETECTOR (NEW)
# -------------------------------------------------
def is_living_entity(word):
    """Detect if word is animal or person using WordNet hypernym paths"""
    synsets = wordnet.synsets(word)
    for syn in synsets:
        for path in syn.hypernym_paths():
            if wordnet.synset('animal.n.01') in path:
                return True
            if wordnet.synset('person.n.01') in path:
                return True
    return False


# -------------------------------------------------
# 📦 LOAD SYMBOL DATA FROM CSV
# -------------------------------------------------
DATASETS_DIR = BASE_DIR / "datasets"
CSV_PATH = BASE_DIR / "datasets" / "cleaned_dream_interpretations.csv"


if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Missing file: {CSV_PATH}")


df_symbols = pd.read_csv(CSV_PATH)
symbol_names = (
    df_symbols["word"]
    .astype(str)
    .str.lower()
    .str.strip()
    .apply(lambda w: lemmatizer.lemmatize(w))
    .tolist()
)


print(f"Loaded {len(symbol_names)} lemmatized symbols from dataset")


# 🔥 STEP 2 — ADD LAZY LOADER ✅ IMPLEMENTED
model = None
symbol_embeddings = None


# 🔴 STEP 3 — PROTECT get_model_and_embeddings()
def get_model_and_embeddings():
    global model, symbol_embeddings

    if model is None:
        try:
            print("[AI] Loading SentenceTransformer model...")
            SentenceTransformer = get_sentence_model()

            if SentenceTransformer is None:
                print("⚠️ Skipping model load")
                return None, None

            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

            print("[AI] Encoding symbol embeddings...")
            symbol_embeddings = model.encode(symbol_names, normalize_embeddings=True)

            print("✅ Model + embeddings ready")

        except Exception as e:
            print("⚠️ Model disabled:", e)
            model = None
            symbol_embeddings = None

    return model, symbol_embeddings


# ✅ FIXED: Proper set operations for CONCRETE_SYMBOLS
CONCRETE_SYMBOLS = set(symbol_names) - set(ABSTRACT_SYMBOLS)
print(f"Concrete symbols count: {len(CONCRETE_SYMBOLS)}")


# -------------------------------------------------
# 🌙 DREAM SIMILARITY DATA  ✅ NEW - FIXED WITH LAZY LOADING
# -------------------------------------------------
DREAMBANK_PATH = BASE_DIR / "datasets" / "dreambank_processed_full.csv"
DREAMBANK_EMBED_PATH = BASE_DIR / "datasets" / "dreambank_embeddings.npy"


print("Loading DreamBank dataset for similarity search...")


dreambank_df = None
dream_similarity_engine = None


# 🔴 STEP 2 — Fix DreamBank initialization
if DREAMBANK_PATH.exists() and DREAMBANK_EMBED_PATH.exists():
    dreambank_df = pd.read_csv(DREAMBANK_PATH)
    dreambank_ids = dreambank_df["number"].tolist()
    dreambank_texts = dreambank_df["semantic_text"].astype(str).tolist()
    dreambank_embeddings = np.load(DREAMBANK_EMBED_PATH)

    print(f"✅ Loaded {len(dreambank_texts)} DreamBank dreams")

    # Initialize similarity engine (model loaded lazily)
    DreamSimilarity = get_dream_similarity()

    if DreamSimilarity:
        model, _ = get_model_and_embeddings()
        dream_similarity_engine = DreamSimilarity(
            model=model,
            dreambank_embeddings=dreambank_embeddings,
            dreambank_texts=dreambank_texts
        )
    else:
        dream_similarity_engine = None
else:
    print("⚠️ DreamBank files not found - similarity search disabled")
    dream_similarity_engine = None


# -------------------------------------------------
# 🧠 ADVANCED SCORING WITH ALL 3 FIXES + LAZY LOADING ✅
# -------------------------------------------------
def compute_hybrid_symbol_scores(dream_text: str):
    """🔧 ALL FIXES: Reduced living boost + Weak filter + Top-200 optimization + LAZY LOADING"""
    # 🔴 STEP 4 — PROTECT THIS FUNCTION TOO
    model, symbol_embeddings = get_model_and_embeddings()

    if model is None or symbol_embeddings is None:
        print("⚠️ Skipping semantic scoring (model unavailable)")
        return []

    dream_embedding = model.encode(dream_text, normalize_embeddings=True)
    embedding_scores = symbol_embeddings @ dream_embedding

    # 🚀 SPEED: Only top 200 symbols by embedding similarity
    top_indices = np.argsort(embedding_scores)[-200:]

    text = dream_text.lower()
    tokens = re.findall(r"\b\w+\b", text)
    dream_words = {lemmatizer.lemmatize(t) for t in tokens}

    words = text.split()
    hybrid_scores = []

    for idx in top_indices:
        symbol = symbol_names[idx]

        # 🔧 FIX #2: Filter weak symbols BEFORE scoring ✅ APPLIED
        if symbol in WEAK_SYMBOLS:
            continue

        base_score = float(embedding_scores[idx])
        symbol_clean = symbol.replace("_", " ")

        # Single words only
        symbol_words = [w.strip() for w in symbol_clean.split()]
        if len(symbol_words) > 1:
            continue

        # Lemma matching
        symbol_word_clean = lemmatizer.lemmatize(symbol_words[0].lower())
        if symbol_word_clean not in dream_words:
            continue

        lexical_boost = 0.0
        repetition_boost = 0.0
        position_boost = 0.0
        concrete_boost = 0.0
        living_boost = 0.0

        # Lexical matching
        if symbol_clean in text:
            lexical_boost += 0.40
            count = text.count(symbol_clean)
            repetition_boost += min(0.20 * count, 0.50)
        else:
            lexical_boost += 0.25

        # Position boost (last 1/3)
        late_text = ' '.join(words[-len(words)//3:])
        if symbol_clean in late_text:
            position_boost += 0.15

        # Concrete/abstract
        if symbol in CONCRETE_SYMBOLS:
            concrete_boost += 0.10
        elif symbol in ABSTRACT_SYMBOLS:
            concrete_boost -= 0.05

        # 🔧 FIX #1: REDUCED LIVING BOOST (0.35 → 0.10) ✅ APPLIED
        if is_living_entity(symbol):
            living_boost += 0.10  # ✅ FIXED

        final_score = (
            base_score + lexical_boost + repetition_boost +
            position_boost + concrete_boost + living_boost
        )
        hybrid_scores.append((symbol, final_score))

    filtered = [(s, v) for s, v in hybrid_scores if v > 0.35]
    return sorted(filtered, key=lambda x: x[1], reverse=True)


def detect_resolution(text: str):
    """Detect narrative resolution"""
    text_lower = text.lower()
    resolution_count = sum(1 for phrase in RESOLUTION_PHRASES if phrase in text_lower)
    return resolution_count > 0


# -------------------------------------------------
# 🚀 FLASK + DB SETUP
# -------------------------------------------------
SECRET_KEY = os.environ.get("REMINDER_SECRET_KEY", "CHANGE_THIS_SECRET")


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'dreams.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["EMAIL_VERIFICATION_ENABLED"] = False


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True


app.config["MAIL_USERNAME"] = "reminderapp2026@gmail.com"
app.config["MAIL_PASSWORD"] = "jodlknbyidzunnyk" 


app.config["MAIL_DEFAULT_SENDER"] = "reminderapp2026@gmail.com"


db = SQLAlchemy(app)
mail = Mail(app)


# -------------------------------------------------
# ✅ UPDATED MODELS WITH DREAM_SIMILARITY
# -------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.String(20))  # ✅ NEW: Date of birth
    age = db.Column(db.String(10))  # ✅ NEW: Age
    nationality = db.Column(db.String(100))  # ✅ NEW: Nationality
    gender = db.Column(db.String(20))  # ✅ NEW: Gender
    religion = db.Column(db.String(20))  # ✅ NEW: Religion (was Star sign)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(200))


class Dream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    mood = db.Column(db.String(50))
    interpretation = db.Column(db.Text)
    symbols = db.Column(db.Text)
    symbol_prominence = db.Column(db.Text)
    avg_symbol_prominence = db.Column(db.Float)
    emotional_arc = db.Column(db.Text)
    confidence = db.Column(db.Text)
    trauma_score = db.Column(db.Float)
    trauma_level = db.Column(db.String(20), default="Low")
    analysis_version = db.Column(db.String(80))
    user_profile_used = db.Column(db.Boolean, default=False)
    dream_similarity = db.Column(db.Float, default=0.0)  # ✅ NEW COLUMN ADDED
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class DreamImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    dream_batch_id = db.Column(db.String(36))


# -------------------------------------------------
# 🏗️ UPDATED MIGRATION WITH DREAM_SIMILARITY
# -------------------------------------------------
def migrate_database():
    try:
        with app.app_context():
            with db.engine.connect() as conn:  # ✅ FIXED: Proper connection context
                result = conn.exec_driver_sql("PRAGMA table_info(dream_image)").fetchall()
                columns = [row[1] for row in result]

                if "dream_batch_id" not in columns:
                    print("🔧 Adding dream_batch_id column...")
                    conn.exec_driver_sql(
                        "ALTER TABLE dream_image ADD COLUMN dream_batch_id VARCHAR(36)"
                    )
                    print("✅ Migration complete!")

                # ✅ NEW: Add profile columns if missing
                user_columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(user)").fetchall()]
                if "is_verified" not in user_columns:
                    conn.exec_driver_sql("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0")

                if "verification_token" not in user_columns:
                    conn.exec_driver_sql("ALTER TABLE user ADD COLUMN verification_token TEXT")
                profile_columns = ["dob", "age", "nationality", "gender", "religion"]

                for col in profile_columns:
                    if col not in user_columns:
                        print(f"🔧 Adding {col} column to user table...")
                        conn.exec_driver_sql(f"ALTER TABLE user ADD COLUMN {col} TEXT")
                        print(f"✅ {col} column added!")

                # ✅ NEW: Add user_profile_used column to dreams table if missing
                dream_columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(dream)").fetchall()]
                if "user_profile_used" not in dream_columns:
                    print("🔧 Adding user_profile_used column to dream table...")
                    conn.exec_driver_sql("ALTER TABLE dream ADD COLUMN user_profile_used BOOLEAN DEFAULT 0")
                    print("✅ user_profile_used column added!")

                # ✅ NEW: Add dream_similarity column if missing
                dream_columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(dream)").fetchall()]
                if "dream_similarity" not in dream_columns:
                    print("🔧 Adding dream_similarity column to dream table...")
                    conn.exec_driver_sql("ALTER TABLE dream ADD COLUMN dream_similarity FLOAT DEFAULT 0")
                    print("✅ dream_similarity column added!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")


# -------------------------------------------------
# 🧠 INIT DB WITH MIGRATION
# -------------------------------------------------
with app.app_context():
    migrate_database()
    db.create_all()


# -------------------------------------------------
# AUTH HELPERS
# -------------------------------------------------
def make_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["user_id"]
    except Exception:
        return None


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        user_id = decode_token(header.split(" ", 1)[1])
        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        request.user_id = user_id
        return f(*args, **kwargs)
    return wrapper


# -------------------------------------------------
# PROFILE ROUTES
# -------------------------------------------------
@app.route("/update_profile", methods=["POST"])
@auth_required
def update_profile():
    """✅ NEW: Update user profile"""
    data = request.get_json() or {}

    dob = data.get("dob")
    age = data.get("age")
    nationality = data.get("nationality")
    gender = data.get("gender")
    religion = data.get("religion")

    user = db.session.get(User, request.user_id)  # ✅ MODERNIZED: db.session.get()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update fields if provided
    if dob is not None:
        user.dob = dob
    if age is not None:
        user.age = age
    if nationality is not None:
        user.nationality = nationality
    if gender is not None:
        user.gender = gender
    if religion is not None:
        user.religion = religion

    db.session.commit()
    return jsonify({"message": "Profile saved successfully"})


@app.route("/get_profile", methods=["GET"])
@auth_required
def get_profile():
    """✅ NEW: Get user profile"""
    user = db.session.get(User, request.user_id)  # ✅ MODERNIZED: db.session.get()
    if not user:
        return jsonify({}), 404

    return jsonify({
        "dob": user.dob,
        "age": user.age,
        "nationality": user.nationality,
        "gender": user.gender,
        "religion": user.religion
    })


# -------------------------------------------------
# 🧠 ENHANCED ANALYSIS WITH PERSONALIZATION + DREAMBANK SIMILARITY ✅
# -------------------------------------------------
def analyze_dream_runtime(dream_text: str, user_id: int, use_profile: bool = True):
    """🔧 ALL FIXES + 🌙 DREAMBANK SIMILARITY + LAZY LOADING"""
    try:
        # ✅ CRITICAL: Get user profile for personalization (MODERNIZED)
        user_profile = None

        if use_profile:
            user = db.session.get(User, user_id)
            if user:
                user_profile = {
                    "gender": user.gender or "unknown",
                    "age": user.age or "unknown",
                    "nationality": user.nationality or "unknown",
                    "religion": user.religion or "unknown"
                }
                print(f"🎯 Using profile for personalization: {user_profile}")
            else:
                print("⚠️ No user profile found - using default interpretation")
        else:
            print("ℹ️ use_profile=False, skipping user profile personalization")

        raw_dominant, emotion_scores, emotion_conf = get_emotion_detector()[0](dream_text)
        
        # -------------------------------------------------
        # 🌙 DREAM SIMILARITY  ✅ NEW - NOW LAZY SAFE
        # -------------------------------------------------
        top_similarity = 0.0
        similar_dream_text = None
        
        if dream_similarity_engine:
            model, _ = get_model_and_embeddings()  # ✅ Ensure model is loaded
            similar_dreams = dream_similarity_engine.find_similar_dreams(dream_text, top_k=1)
            if similar_dreams:
                top_similarity = similar_dreams[0]["similarity_score"]
                similar_dream_text = similar_dreams[0]["dream_text"]
                print(f"🌙 Found similar dream (similarity: {top_similarity:.3f})")
        else:
            print("⚠️ DreamBank similarity disabled")

        trajectory = get_emotion_detector()[1](dream_text)
        dominant_emotion = trajectory.get("overall_emotion", raw_dominant)

        ranked_symbols = compute_hybrid_symbol_scores(dream_text)
        raw_symbols = {s: float(v) for s, v in ranked_symbols[:10]}

        has_resolution = detect_resolution(dream_text)
        insight = get_symbol_insight()(raw_symbols, dominant_emotion, dream_text)
        grounded_symbols = insight.get("symbol_scores", {})

        if not grounded_symbols:
            grounded_symbols = dict(list(raw_symbols.items())[:3])

        dream_words = set(re.findall(r"\b\w+\b", dream_text.lower()))
        filtered_symbols = {
            s: v for s, v in grounded_symbols.items()
            if any(word in s.lower() for word in dream_words)
        }

        if filtered_symbols:
            grounded_symbols = filtered_symbols

        if len(grounded_symbols) < 3:
            grounded_symbols = raw_symbols

        # 🔧 ALL FIXES: Complete protection against empty dictionaries
        if not grounded_symbols:
            top_symbols = {}
            symbol_prominence = {}
            avg_symbol_prominence = 0.0
        else:
            # 🔧 FIX #3: Normalize top 5 symbols to 1.00 max scale ✅ APPLIED
            ranked_top = sorted(grounded_symbols.items(), key=lambda x: x[1], reverse=True)[:12]
            if ranked_top:
                max_score = max(v for _, v in ranked_top) or 1
                top_symbols = {
                    s: round(v / max_score, 2)  # ✅ Scales highest to 1.00
                    for s, v in ranked_top
                }
            else:
                top_symbols = {}

            # 🔧 FIX #5: Complete fallback protection
            if not top_symbols:
                symbol_prominence = {}
                avg_symbol_prominence = 0.0
            else:
                total_score = sum(top_symbols.values()) or 1
                symbol_prominence = {
                    s: round((v / total_score) * 100, 2)
                    for s, v in top_symbols.items()
                }

                # 🔧 FIX #4: Protect avg_symbol_prominence from empty dict
                if symbol_prominence:
                    avg_symbol_prominence = round(sum(symbol_prominence.values()) / len(symbol_prominence), 2)
                else:
                    avg_symbol_prominence = 0.0

        print("\n🎯 NORMALIZED SYMBOL SCORES (v11 - LAZY LOADED):")
        for s, v in top_symbols.items():
            print(f"  {s:<12} {v:>5.2f}")
        print(f"  📊 Avg Prominence: {avg_symbol_prominence:.1f}%")

        dynamics = get_resolve_dynamics()(insight, dream_text)
        dynamic_names = [d["dynamic"] for d in dynamics if isinstance(d, dict)]

        emotion_distribution = trajectory.get("emotion_distribution", {"neutral": 1.0})
        threat_count = sum(1 for d in dynamic_names if "threat" in d)
        repeated_threats = threat_count >= 2

        trauma_score, trauma_level = get_trauma_signal()(
            emotion_scores=emotion_distribution,
            dynamics=dynamic_names,
            no_resolution=not has_resolution,
            repeated_threats=repeated_threats,
            emotion_variance=float(np.var(list(emotion_distribution.values()))) if emotion_distribution else 0.0,
            recurring_count=sum(1 for s, score in raw_symbols.items() if score > 0.5)
        )

        symbol_conf, overall_conf = get_confidence_utils()
        symbol_conf = symbol_conf(grounded_symbols)
        overall_conf = overall_conf(
            symbol_conf,
            emotion_conf,
            len(grounded_symbols)
        )

        # ✅ CRITICAL: Pass user_profile to generate_interpretation
        interpretation = get_interpretation()(
            dynamics=dynamics,
            dream_text=dream_text,
            dominant_emotion=dominant_emotion,
            top_symbols=list(top_symbols.keys()),
            has_resolution=has_resolution,
            user_profile=user_profile  # 🎯 THIS IS THE MISSING PIECE!
        )

        # ✅ FIXED: Return actual profile usage status
        profile_was_used = bool(user_profile)

        return {
            "dominant_emotion": str(dominant_emotion),
            "trajectory": ensure_json(trajectory),
            "symbols": ensure_json(top_symbols),  # ✅ Normalized 0-1 scale
            "symbol_prominence": symbol_prominence,  # ✅ Percentage scale
            "avg_symbol_prominence": avg_symbol_prominence,
            "interpretation": ensure_string(interpretation),
            
            # ✅ NEW: DreamBank similarity results
            "dream_similarity": round(top_similarity, 2),
            "similar_dream_example": similar_dream_text[:200] if similar_dream_text else None,
            
            "confidence": {
                "symbol": round(symbol_conf * 100, 2),
                "overall": round(overall_conf * 100, 2),
            },
            "trauma_score": float(trauma_score),
            "trauma_level": trauma_level,
            "analysis_version": "v12_lazy_model",  # ✅ Updated version with lazy loading
            "user_profile_used": profile_was_used  # ✅ CORRECT: Actual boolean value
        }
    except Exception as e:
        print("ANALYZER ERROR:", str(e))
        traceback.print_exc()
        return {
            "dominant_emotion": "neutral",
            "trajectory": {},
            "symbols": {},
            "symbol_prominence": {},
            "avg_symbol_prominence": 0.0,
            "interpretation": "Analysis encountered an issue. The dream reflects complex emotional processing.",
            "dream_similarity": 0.0,  # ✅ Added to fallback
            "similar_dream_example": None,
            "confidence": {"symbol": 0.0, "overall": 0.0},
            "trauma_score": 0.0,
            "trauma_level": "Low",
            "analysis_version": "dream_analyzer_safe_fallback",
            "user_profile_used": False
        }


# -------------------------------------------------
# IMAGE ROUTES - ✅ FIXED get_visualizations ENDPOINT
# -------------------------------------------------
@app.route("/dream_images/<path:filename>")
def serve_dream_image(filename):
    return send_from_directory(BASE_DIR / "dream_output", filename)


@app.route("/get_visualizations", methods=["GET"])
@auth_required
def get_visualizations():
    """✅ FIXED: Enrich ALL batches with dream_text - SIMPLE IMPLEMENTATION"""
    try:
        images = DreamImage.query.filter_by(user_id=request.user_id)\
            .order_by(DreamImage.created_at.desc()).all()

        batches = {}
        for img in images:
            batch_id = img.dream_batch_id or f"single_{img.id}"
            if batch_id not in batches:
                batches[batch_id] = {
                    "id": batch_id,
                    "images": [],
                    "count": 0,
                    "created_at": img.created_at.isoformat() if img.created_at else None
                }
            batches[batch_id]["images"].append({
                "url": img.image_url,
                "id": img.id
            })
            batches[batch_id]["count"] += 1

        batch_list = sorted(
            batches.values(),
            key=lambda x: x["created_at"] or "1970-01-01",
            reverse=True
        )

        # ✅ SIMPLE FIX: Add dream_text to ALL batches (empty string for old batches)
        for batch in batch_list:
            batch["dream_text"] = ""  # Empty string - frontend will show nothing for old batches

        return jsonify(batch_list)
    except Exception as e:
        print(f"ERROR in get_visualizations: {e}")
        return jsonify([]), 500


@app.route("/delete_dream_batch/<dream_batch_id>", methods=["DELETE"])
@auth_required
def delete_dream_batch(dream_batch_id):
    try:
        images = DreamImage.query.filter_by(
            user_id=request.user_id,
            dream_batch_id=dream_batch_id
        ).all()

        if not images:
            return jsonify({"error": "Batch not found"}), 404

        for img in images:
            db.session.delete(img)

        db.session.commit()
        return jsonify({"message": f"Deleted {len(images)} images from batch"})
    except Exception as e:
        print(f"ERROR in delete_dream_batch: {e}")
        db.session.rollback()
        return jsonify({"error": "Delete failed"}), 500


@app.route("/visualize_dream", methods=["POST"])
@auth_required
def visualize_dream():
    data = request.get_json() or {}
    dream_text = data.get("dream", "").strip()

    if not dream_text:
        return jsonify({"error": "Dream text required"}), 400

    dream_batch_id = str(uuid.uuid4())
    request_id = uuid.uuid4().hex[:8]

    scenes = get_scene_splitter()(
        dream_text,
        chunk_size=50,
        max_scenes=3
    )

    image_urls = []
    base_url = "http://127.0.0.1:5000"

    for i, scene in enumerate(scenes):
        is_final = (i == len(scenes) - 1)
        prompt = get_prompt_builder()(scene, is_final=is_final)
        unique_index = f"{request_id}_{i}"
        filename = get_image_generator()(prompt, unique_index)

        image_url = f"{base_url}/dream_images/{filename.name}"
        image_urls.append(image_url)

        img = DreamImage(
            image_url=image_url,
            user_id=request.user_id,
            dream_batch_id=dream_batch_id
        )
        db.session.add(img)

    db.session.commit()

    return jsonify({
        "images": image_urls,
        "dream_batch_id": dream_batch_id
    })


# -------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    email = data.get("email", "").lower().strip()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not email or not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    token = str(uuid.uuid4())

    if app.config["EMAIL_VERIFICATION_ENABLED"]:
        user = User(
            email=email,
            username=username,
            password_hash=pw_hash,
            is_verified=False,
            verification_token=token
        )

        verify_link = f"http://localhost:5000/verify/{token}"

        try:
            msg = Message(
                subject="Verify your REMinder account",
                recipients=[email]
            )

            msg.body = f"""
Welcome to REMinder!

Click the link below to verify your account:

{verify_link}

If you didn't sign up, ignore this email.
"""

            mail.send(msg)

            print(f"✅ Email sent to {email}")

        except Exception as e:
            print(f"❌ Email failed: {e}")
            print(f"VERIFY LINK (fallback): {verify_link}")

    else:
        user = User(
            email=email,
            username=username,
            password_hash=pw_hash,
            is_verified=True
        )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created",
        "verification_required": app.config["EMAIL_VERIFICATION_ENABLED"]
    }), 201


@app.route("/verify/<token>")
def verify_email(token):
    if not app.config["EMAIL_VERIFICATION_ENABLED"]:
        return "Verification disabled"

    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return "Invalid or expired token"

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return redirect("http://localhost:3000/login?verified=true")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    if app.config["EMAIL_VERIFICATION_ENABLED"] and not user.is_verified:
        return jsonify({"error": "Please verify your email first"}), 403

    return jsonify({
        "token": make_token(user.id),
        "user": {"id": user.id, "email": user.email, "username": user.username}
    })


# -------------------------------------------------
# 💭 DREAM ROUTES - ✅ FULLY UPDATED WITH DREAMBANK SIMILARITY + LAZY LOADING!
# -------------------------------------------------
@app.route("/add_dream", methods=["POST"])
@auth_required
def add_dream():
    data = request.get_json() or {}
    content = data.get("content", "").strip()
    title = data.get("title", "Untitled Dream")

    # ✅ NEW: allow frontend to choose whether to use profile
    use_profile = data.get("use_profile", True)

    if not content:
        return jsonify({"error": "Dream content required"}), 400

    try:
        # ✅ CRITICAL: Pass user_id and use_profile to analysis function
        result = analyze_dream_runtime(content, request.user_id, use_profile)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Dream analysis failed"}), 500

    dream = Dream(
        title=title,
        content=content,
        mood=str(result["dominant_emotion"]),
        interpretation=ensure_string(result["interpretation"]),
        symbols=json.dumps(ensure_json(result["symbols"])),
        symbol_prominence=json.dumps(result["symbol_prominence"]),
        avg_symbol_prominence=result["avg_symbol_prominence"],
        emotional_arc=json.dumps(ensure_json(result["trajectory"])),
        confidence=json.dumps(ensure_json(result["confidence"])),
        trauma_score=float(result["trauma_score"]),
        trauma_level=result.get("trauma_level", "Low"),
        analysis_version=result["analysis_version"],
        user_profile_used=result["user_profile_used"],
        dream_similarity=result.get("dream_similarity", 0.0),  # ✅ NEW: NOW STORED IN DB
        user_id=request.user_id
    )

    db.session.add(dream)
    db.session.commit()

    return jsonify({
        "message": "Dream saved with personalized interpretation + DreamBank similarity + LAZY MODEL",
        "profile_used": result.get("user_profile_used", False),
        "dream_similarity": result.get("dream_similarity",
        0.0)  # ✅ NEW
    }), 201


@app.route("/get_dreams", methods=["GET"])
@auth_required
def get_dreams():
    dreams = Dream.query.filter_by(user_id=request.user_id)\
        .order_by(Dream.date.desc()).all()

    return jsonify([
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "date": d.date.isoformat(),
            "mood": d.mood,
            "interpretation": d.interpretation,
            "symbols": json.loads(d.symbols) if d.symbols else {},
            "symbol_prominence": json.loads(d.symbol_prominence) if d.symbol_prominence else {},
            "avg_symbol_prominence": d.avg_symbol_prominence,
            "emotional_arc": json.loads(d.emotional_arc) if d.emotional_arc else {},
            "confidence": json.loads(d.confidence) if d.confidence else {},
            "trauma_score": d.trauma_score,
            "trauma_level": getattr(d, "trauma_level", "Low"),
            "analysis_version": d.analysis_version,
            "user_profile_used": d.user_profile_used,
            
            # ✅ FIXED: Now stored in DB column - direct access
            "dream_similarity": d.dream_similarity,
            "similar_dream_example": getattr(d, "similar_dream_example", None)  # still only in runtime
        }
        for d in dreams
    ])


@app.route("/delete_dream/<int:dream_id>", methods=["DELETE"])
@auth_required
def delete_dream(dream_id):
    dream = db.session.get(Dream, dream_id)  # ✅ MODERNIZED
    if not dream:
        return jsonify({"error": "Dream not found"}), 404
    if dream.user_id != request.user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(dream)
    db.session.commit()
    return jsonify({"message": "Dream deleted"})


chatbot_bp = get_chatbot_bp()
app.register_blueprint(chatbot_bp)

@app.route("/")
def home():
    return "REMinder API is running 🚀"


if __name__ == "__main__":
    import os

    print("🚀 Server starting...")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )

