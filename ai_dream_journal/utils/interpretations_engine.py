import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List
import spacy
from sentence_transformers import SentenceTransformer, util

# --- CORRECTED IMPORTS ---
from .knowledge.roles import SYMBOL_ROLES
from .knowledge.roles_to_force import ROLE_TO_FORCE
from .knowledge.emotion_utils import detect_emotion
from .knowledge.symbol_weights import load_symbol_weights

EMOTION_TO_FORCE = {
    "fear": "fear",
    "anxiety": "fear",
    "nervous": "fear",
    "panic": "fear",
    "anger": "control",
    "relief": "release"
}

SYMBOL_BASE_WEIGHTS = load_symbol_weights()
SEMANTIC_MATCH_THRESHOLD = 0.68

_NLP = None
_SBERT = None
_SYMBOL_EMBEDDINGS = None

def get_nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm")
    return _NLP

def get_sbert():
    global _SBERT
    if _SBERT is None:
        _SBERT = SentenceTransformer("all-MiniLM-L6-v2")
    return _SBERT

def get_symbol_embeddings():
    global _SYMBOL_EMBEDDINGS
    if _SYMBOL_EMBEDDINGS is None:
        model = get_sbert()
        symbols = list(SYMBOL_ROLES.keys())
        embeddings = model.encode(symbols, convert_to_tensor=True)
        _SYMBOL_EMBEDDINGS = dict(zip(symbols, embeddings))
    return _SYMBOL_EMBEDDINGS

def match_symbol_semantically(word: str) -> str | None:
    model = get_sbert()
    symbol_embeddings = get_symbol_embeddings()

    word_emb = model.encode(word, convert_to_tensor=True)

    best_match = None
    best_score = 0.0

    for sym, emb in symbol_embeddings.items():
        score = util.cos_sim(word_emb, emb).item()
        if score > best_score:
            best_score = score
            best_match = sym

    if best_score >= SEMANTIC_MATCH_THRESHOLD:
        return best_match

    return None

@dataclass
class SymbolInstance:
    symbol: str          # canonical symbol (fog)
    surface: str         # actual word in dream (mist)
    role: str
    force: str
    weight: float

@dataclass
class Scene:
    text: str
    symbols: List[SymbolInstance]
    emotion: str | None

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    return text.strip()

TRANSITION_MARKERS = {
    "then", "suddenly", "after that", "later", "next"
}

def segment_into_scenes(text: str) -> List[str]:
    sentences = re.split(r"[.!?]", text)
    scenes = []
    current = []

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        if any(marker in s for marker in TRANSITION_MARKERS):
            if current:
                scenes.append(" ".join(current))
                current = []

        current.append(s)

    if current:
        scenes.append(" ".join(current))

    return scenes

def extract_symbols(scene_text: str) -> List[tuple[str, str]]:
    nlp = get_nlp()
    doc = nlp(scene_text)

    found_direct = set()
    found_semantic = set()
    symbol_set = set(SYMBOL_ROLES.keys())

    for token in doc:
        lemma = token.lemma_.lower()
        surface = token.text.lower()

        if lemma in symbol_set:
            found_direct.add((lemma, surface))
        else:
            if token.pos_ == "NOUN" and not token.is_stop:
                matched = match_symbol_semantically(lemma)
                if matched:
                    # DEBUG: semantic match
                    # print(f"[SEMANTIC MATCH] {surface} → {matched}")
                    found_semantic.add((matched, surface))

    # 🔑 PRIORITY RULE: direct symbols always win
    if found_direct:
        return list(found_direct)

    return list(found_semantic)

def build_symbol_instances(scene_text: str) -> List[SymbolInstance]:
    instances = []

    raw_symbols = extract_symbols(scene_text)
    emotion = detect_emotion(scene_text)

    seen = set()
    for canonical_sym, surface_sym in raw_symbols:
        if canonical_sym in seen:
            continue
        seen.add(canonical_sym)

        role = SYMBOL_ROLES[canonical_sym]
        force = ROLE_TO_FORCE.get(role, "unknown")

        weight = SYMBOL_BASE_WEIGHTS.get(canonical_sym, 1.0)

        # repetition boost (check surface form occurrences)
        if scene_text.count(surface_sym) > 1:
            weight += 1.0
        # emotion proximity boost
        if emotion:
            weight += 0.75

        instances.append(
            SymbolInstance(
                symbol=canonical_sym,
                surface=surface_sym,
                role=role,
                force=force,
                weight=weight
            )
        )

    return instances

def extract_dominant_forces(scenes: List[Scene]) -> List[str]:
    scores = defaultdict(float)

    for scene in scenes:
        for sym in scene.symbols:
            scores[sym.force] += sym.weight

        # 🔑 emotion introduces force
        if scene.emotion and scene.emotion in EMOTION_TO_FORCE:
            emotion_force = EMOTION_TO_FORCE[scene.emotion]
            scores[emotion_force] += 1.5

    return sorted(scores, key=scores.get, reverse=True)

def detect_conflicts(forces: List[str]) -> List[str]:
    conflicts = []

    if "change" in forces and "fear" in forces:
        conflicts.append("movement versus fear")

    if "control" in forces and "uncertainty" in forces:
        conflicts.append("control versus uncertainty")

    return conflicts

def describe_symbols(scenes: List[Scene]) -> List[str]:
    descriptions = []

    role_groups = defaultdict(list)

    for scene in scenes:
        for sym in scene.symbols:
            role_groups[sym.role].append(sym.symbol)

    for role, symbols in role_groups.items():
        unique = list(dict.fromkeys(symbols))  # preserve order

        if role == "transition":
            descriptions.append(
                f"The presence of {unique[0]} places the dreamer in a moment of transition."
            )

        elif role in {"obscured_perception", "uncertainty"}:
            joined = " and ".join(unique)
            descriptions.append(
                f"The imagery of {joined} reduces clarity and visibility."
            )

        elif role == "pressure":
            descriptions.append(
                f"Actions involving {unique[0]} introduce pressure and urgency."
            )

        elif role == "loss_of_control":
            descriptions.append(
                f"The image of {unique[0]} suggests instability or loss of control."
            )

        elif role == "cleansing":
            descriptions.append(
                f"The presence of {unique[0]} suggests emotional release or renewal."
            )

    descriptions.sort(
        key=lambda s: 0 if "transition" in s else 1
    )

    return descriptions

def synthesize_interpretation(
    scenes: List[Scene],
    forces: List[str],
    conflicts: List[str]
) -> str:

    parts = []

    # --- Opening: early scene ---
    if scenes:
        early_symbols = describe_symbols([scenes[0]])
        if early_symbols:
            joined = " ".join(s.lower() for s in early_symbols[:2])
            parts.append(
                f"At the beginning of the dream, {joined}"
            )

    # --- Middle development ---
    # --- Single-scene handling ---
    if len(scenes) == 1:
         parts.append(
        "The dream remains within a single psychological situation without clear progression or resolution."
            )

    if len(scenes) > 1:
        mid_symbols = describe_symbols(scenes[1:-1])
        if mid_symbols:
            parts.append(
                f"As the dream progresses, {mid_symbols[0].lower()}"
            )

    # --- Ending emphasis ---
    if len(scenes) > 1:
        end_symbols = describe_symbols([scenes[-1]])
        if end_symbols:
            parts.append(
                f"The dream concludes with imagery where {end_symbols[0].lower()}"
            )

    # --- Trajectory ---
    trajectory = detect_trajectory(scenes)
    if trajectory:
        parts.append(
            f"Overall, the emotional movement of the dream reflects a {trajectory}."
        )

    # --- Conflict ---
    for conflict in conflicts:
        parts.append(
            f"This creates a psychological tension characterized by {conflict}."
        )

    # --- Closing ---
    parts.append(
        "The dream does not resolve this tension directly, suggesting the underlying issue remains active in waking life."
    )

    return " ".join(parts)

def scene_position(index: int, total: int) -> str:
    if index == 0:
        return "beginning"
    elif index == total - 1:
        return "ending"
    return "middle"

def extract_scene_forces(scene: Scene) -> dict[str, float]:
    forces = defaultdict(float)
    for sym in scene.symbols:
        forces[sym.force] += sym.weight

    if scene.emotion and scene.emotion in EMOTION_TO_FORCE:
        forces[EMOTION_TO_FORCE[scene.emotion]] += 1.5

    return forces

def detect_trajectory(scenes: List[Scene]) -> str | None:
    if len(scenes) < 2:
        return None

    first = extract_scene_forces(scenes[0])
    last = extract_scene_forces(scenes[-1])

    if not first or not last:
        return None

    first_force = max(first, key=first.get)
    last_force = max(last, key=last.get)

    if first_force != last_force:
        return f"shift from {first_force} to {last_force}"

    return f"persistent {first_force}"

def interpret_dream(dream_text: str) -> str:
    text = preprocess_text(dream_text)
    scene_texts = segment_into_scenes(text)

    scenes = []
    for st in scene_texts:
        symbols = build_symbol_instances(st)
        emotion = detect_emotion(st)
        scenes.append(Scene(text=st, symbols=symbols, emotion=emotion))

    forces = extract_dominant_forces(scenes)
    conflicts = detect_conflicts(forces)

    return synthesize_interpretation(scenes, forces, conflicts)

if __name__ == "__main__":
    dream = (
        "I was walking across a bridge at night. "
        "Thick fog surrounded me and I felt nervous."
    )
    print(interpret_dream(dream))
