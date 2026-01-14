# app.py — FINAL AUTH + DREAM_ANALYZER + IMAGE VISUALIZATION (IMPORT ORDER FIXED)

import sys
from pathlib import Path

# -------------------------------------------------
# 🔧 PATH SETUP (MUST BE FIRST)
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

ANALYZER_DIR = BASE_DIR / "dream_Analyzer"
VISUALIZER_DIR = BASE_DIR / "dream_visualizer"

sys.path.insert(0, str(ANALYZER_DIR))
sys.path.insert(0, str(VISUALIZER_DIR))

# -------------------------------------------------
# NOW SAFE TO IMPORT EVERYTHING
# -------------------------------------------------
import json
import traceback
import os
import sqlite3
from datetime import datetime, timedelta
import uuid

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import jwt
import bcrypt
from functools import wraps

# ✅ NOW THESE WORK (path setup happened first)
from scene_splitter import split_into_scenes
from prompt_builder import build_prompt
from image_generator import generate_image

# -------------------------------------------------
# ✅ IMPORTS — EXACTLY FROM dream_analyzer
# -------------------------------------------------
import numpy as np
from sentence_transformers import SentenceTransformer

from trauma_signal import trauma_linked_score
from symbol_insight import build_symbol_insight
from resolve_dynamics import resolve_symbol_emotion_dynamics
from interpretation_generator import generate_interpretation
from emotion_detector import (
    detect_emotion_with_scores,
    detect_emotion_trajectory
)
from confidence_utils import (
    compute_symbol_confidence,
    compute_overall_confidence
)

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
# 📦 LOAD SYMBOL DATA
# -------------------------------------------------
DATASETS_DIR = BASE_DIR / "datasets"

SYMBOL_EMB_PATH = DATASETS_DIR / "symbol_embeddings.npy"
SYMBOL_META_PATH = DATASETS_DIR / "symbol_metadata.json"

if not SYMBOL_EMB_PATH.exists():
    raise FileNotFoundError(f"Missing file: {SYMBOL_EMB_PATH}")

if not SYMBOL_META_PATH.exists():
    raise FileNotFoundError(f"Missing file: {SYMBOL_META_PATH}")

symbol_embeddings = np.load(SYMBOL_EMB_PATH)

with open(SYMBOL_META_PATH, "r", encoding="utf-8") as f:
    symbol_names = json.load(f)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# -------------------------------------------------
# 🚀 FLASK + DB SETUP
# -------------------------------------------------
SECRET_KEY = os.environ.get("REMINDER_SECRET_KEY", "CHANGE_THIS_SECRET")

app = Flask(__name__)
CORS(app)

DB_PATH = BASE_DIR / "dreams.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -------------------------------------------------
# 🧱 MODELS
# -------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    mood = db.Column(db.String(50))
    interpretation = db.Column(db.Text)
    symbols = db.Column(db.Text)
    emotional_arc = db.Column(db.Text)
    confidence = db.Column(db.Text)
    trauma_score = db.Column(db.Float)

    analysis_version = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

# -------------------------------------------------
# 🏗️ INIT
# -------------------------------------------------
with app.app_context():
    db.create_all()

# -------------------------------------------------
# 🔐 AUTH HELPERS
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
# 🧠 ANALYSIS CORE (FROM test.py) — FIXED RETURN
# -------------------------------------------------
def analyze_dream_runtime(dream_text: str):
    dominant_emotion, emotion_scores, emotion_conf = (
        detect_emotion_with_scores(dream_text)
    )

    trajectory = detect_emotion_trajectory(dream_text)

    dream_embedding = model.encode(dream_text, normalize_embeddings=True)
    scores = symbol_embeddings @ dream_embedding

    ranked = sorted(
        zip(symbol_names, scores),
        key=lambda x: x[1],
        reverse=True
    )

    raw_symbols = {s: float(v) for s, v in ranked[:5]}

    insight = build_symbol_insight(raw_symbols, dominant_emotion, dream_text)
    grounded_symbols = insight.get("symbol_scores", {})

    symbol_conf = compute_symbol_confidence(grounded_symbols)
    overall_conf = compute_overall_confidence(symbol_conf, emotion_conf)

    dynamics = resolve_symbol_emotion_dynamics(insight, dream_text)
    dynamic_names = [d["dynamic"] for d in dynamics if isinstance(d, dict)]

    interpretation = generate_interpretation(
        dynamics=dynamics,
        dream_text=dream_text,
        dominant_emotion=dominant_emotion
    )

    trauma_score = trauma_linked_score(
        emotion_scores=emotion_scores,
        dynamics=dynamic_names,
        no_resolution=True,
        repeated_threats=False,
        emotion_variance=float(np.var(list(emotion_scores.values()))),
        recurring_count=0
    )

    return {
        "dominant_emotion": str(dominant_emotion),
        "trajectory": ensure_json(trajectory),
        "symbols": ensure_json(grounded_symbols),
        "interpretation": ensure_string(interpretation),
        "confidence": {
            "symbol": float(symbol_conf) if isinstance(symbol_conf, (int, float)) else 0.0,
            "overall": float(overall_conf) if isinstance(overall_conf, (int, float)) else 0.0,
        },
        "trauma_score": float(trauma_score) if trauma_score is not None else 0.0,
        "analysis_version": "dream_analyzer_test_equivalent"
    }

# -------------------------------------------------
# 🖼️ IMAGE SERVING ROUTE (ABSOLUTE PATH)
# -------------------------------------------------
@app.route("/dream_images/<path:filename>")
def serve_dream_image(filename):
    return send_from_directory(
        BASE_DIR / "dream_output",
        filename
    )

# -------------------------------------------------
# 🔑 AUTH ROUTES
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
        return jsonify({"error": "Email exists"}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(email=email, username=username, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "token": make_token(user.id),
        "user": {"id": user.id, "email": user.email, "username": user.username}
    })

# -------------------------------------------------
# 🌙 DREAM ROUTES
# -------------------------------------------------
@app.route("/add_dream", methods=["POST"])
@auth_required
def add_dream():
    data = request.get_json() or {}
    content = data.get("content", "").strip()
    title = data.get("title", "Untitled Dream")

    if not content:
        return jsonify({"error": "Dream content required"}), 400

    try:
        result = analyze_dream_runtime(content)
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Dream analysis failed"}), 500

    dream = Dream(
        title=title,
        content=content,
        mood=str(result["dominant_emotion"]),
        interpretation=ensure_string(result["interpretation"]),
        symbols=json.dumps(ensure_json(result["symbols"])),
        emotional_arc=json.dumps(ensure_json(result["trajectory"])),
        confidence=json.dumps(ensure_json(result["confidence"])),
        trauma_score=float(result["trauma_score"]),
        analysis_version=result["analysis_version"],
        user_id=request.user_id
    )

    db.session.add(dream)
    db.session.commit()

    return jsonify({"message": "Dream saved"}), 201

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
            "emotional_arc": json.loads(d.emotional_arc) if d.emotional_arc else {},
            "confidence": json.loads(d.confidence) if d.confidence else {},
            "trauma_score": d.trauma_score,
            "analysis_version": d.analysis_version
        }
        for d in dreams
    ])

@app.route("/delete_dream/<int:dream_id>", methods=["DELETE"])
@auth_required
def delete_dream(dream_id):
    dream = Dream.query.get_or_404(dream_id)
    if dream.user_id != request.user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(dream)
    db.session.commit()
    return jsonify({"message": "Dream deleted"})

# -------------------------------------------------
# 🖼️ FAST IMAGE GENERATION ENDPOINT (PRODUCTION SAFE)
# -------------------------------------------------
@app.route("/visualize_dream", methods=["POST"])
@auth_required
def visualize_dream():
    data = request.get_json() or {}
    dream_text = data.get("dream", "").strip()

    if not dream_text:
        return jsonify({"error": "Dream text required"}), 400

    request_id = uuid.uuid4().hex[:8]

    scenes = split_into_scenes(
        dream_text,
        chunk_size=50,
        max_scenes=3   # KEEP THIS LOW FOR SPEED
    )

    image_urls = []
    base_url = "http://127.0.0.1:5000"


    for i, scene in enumerate(scenes):
        is_final = (i == len(scenes) - 1)
        prompt = build_prompt(scene, is_final=is_final)
        unique_index = f"{request_id}_{i}"
        filename = generate_image(prompt, unique_index)

        image_urls.append(
            f"{base_url}/dream_images/{filename.name}"
        )

    return jsonify({
        "images": image_urls
    })

# -------------------------------------------------
# ▶️ RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
