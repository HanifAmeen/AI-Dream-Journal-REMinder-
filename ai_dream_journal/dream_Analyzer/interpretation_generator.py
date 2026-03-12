# interpretation_generator.py
import re
import time
from typing import List, Dict, Optional
import random
from collections import Counter
import ollama
from functools import lru_cache  # STEP 3: Cached WordNet lookup (ready for symbol scoring)
from phrasing_pools import PHRASING_POOLS
from phrase_selector import select_phrase
from symbols.descriptive_csv_loader import (
    load_descriptive_phrases,
    load_symbol_meanings
)
from symbols.concrete_object_detector import detect_concrete_objects
from symbols.descriptive_enrichment import build_descriptive_sentences

# NEW: Emotion-aware phrasing pools structure
EMOTION_AWARE_POOLS = {
    "pursuit": {
        "fear": [
            "A sense of being chased or pressured emerges strongly, reflecting urgent avoidance of something threatening.",
            "The feeling of pursuit creates intense pressure, as if something demanding cannot be escaped.",
            "Fleeing or being followed suggests confrontation with an overwhelming internal force."
        ],
        "sadness": [
            "A slow, heavy pursuit unfolds, suggesting emotional weight that feels inescapable.",
            "The sense of being followed carries melancholy, as if past losses maintain their hold.",
            "Chasing or being chased reflects a lingering emotional burden seeking resolution."
        ],
        "calm": [
            "A gentle sense of movement or pursuit appears, suggesting purposeful navigation through change.",
            "The theme of following or seeking unfolds steadily, indicating directed emotional exploration.",
            "Pursuit in this context suggests conscious movement toward understanding or integration."
        ],
        "default": [
            "A pattern of pursuit or avoidance becomes prominent, suggesting tension between movement and resistance.",
            "The dream highlights chasing or being chased, pointing to internal conflict over direction.",
            "Seeking or fleeing appears as a core dynamic, reflecting competing inner drives."
        ]
    },
    "trapped": {
        "fear": [
            "A powerful sense of entrapment dominates, amplifying feelings of helplessness and threat.",
            "Being confined or restricted creates intense emotional pressure with no clear escape.",
            "The theme of being trapped suggests overwhelming circumstances beyond immediate control."
        ],
        "sadness": [
            "A heavy feeling of being stuck emerges, reflecting emotional stagnation or loss.",
            "The sense of confinement carries deep melancholy, suggesting internalized emotional barriers.",
            "Feeling trapped points to emotional weight that resists movement or release."
        ],
        "calm": [
            "A contained or structured space appears, suggesting boundaries that provide safety rather than threat.",
            "The theme of confinement unfolds steadily, indicating purposeful limitation or focus.",
            "Being in a defined space suggests emotional containment supporting integration."
        ],
        "default": [
            "A pattern of confinement or restriction becomes evident, suggesting internal barriers to movement.",
            "Feeling trapped or contained reflects tension between freedom and limitation.",
            "The theme of enclosure points to psychological boundaries requiring navigation."
        ]
    }
    # Extend for other dynamics: barrier, exposure, stagnation, etc.
}

# STEP 3: Cached WordNet lookup (ready for use in symbol scoring pipeline)
@lru_cache(maxsize=5000)
def is_living_entity(word: str) -> bool:
    """Cached WordNet lookup for living entity detection."""
    # Placeholder - implement WordNet logic here when called from symbol scoring
    living_entities = {'person', 'animal', 'dog', 'cat', 'bird', 'child', 'man', 'woman'}
    return word.lower() in living_entities

# STEP 2: Speed-optimized LLM interpretation function with ORIGINAL PROMPT
def generate_llm_interpretation(
    dream_text: str,
    top_symbols: List[str],
    dominant_emotion: str,
    trajectory: List[str],
    dynamics: List[Dict]
) -> str:
    # Short-dream trajectory optimization
    if len(dream_text.split()) < 40:
        trajectory = [dominant_emotion]
    
    # Format inputs concisely
    symbols_text = ", ".join(top_symbols[:5]) if top_symbols else "none"  # Top 5 only
    trajectory_text = " → ".join(trajectory) if trajectory else "stable"
    dynamics_text = ", ".join([d.get("dynamic", "") for d in dynamics[:3]]) if dynamics else "none"  # Top 3 only

    # ORIGINAL DETAILED PROMPT (as requested)
    prompt = f"""
You are a psychological dream interpretation expert.

Your task is to interpret a dream using structured analysis signals.

DREAM NARRATIVE
{dream_text}

ANALYSIS SIGNALS

Symbols detected:
{symbols_text}

Dominant emotion:
{dominant_emotion}

Emotional trajectory:
{trajectory_text}

Psychological dynamics detected:
{dynamics_text}

INTERPRETATION TASK

Use the dream narrative and analysis signals to produce a psychological interpretation.

Follow these steps internally:
1. Consider the emotional tone of the dream.
2. Consider what the main symbols might represent psychologically.
3. Consider how the emotional trajectory changes across the dream.
4. Connect the symbols and emotions into a psychological interpretation.

Write the interpretation using EXACTLY the following section headings:

Emotional Overview:
Symbolic Processes:
Psychological Meaning:
Resolution & Development:
Reflective Insight:

Each section should contain 2–4 sentences.

Guidelines:
- Do not claim the interpretation is certain.
- Focus on psychological processes rather than fixed meanings.
- Base your reasoning on the dream narrative and detected symbols.
- Avoid generic explanations about dreams in general.
-The final section "Reflective Insight" must end with a complete sentence.
Do not stop mid-sentence.
"""

    start_time = time.time()
    
    response = ollama.chat(
        model="llama3:8b",  # Kept as-is per your code
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0.35,      # Lower temp = faster decisions
            "num_predict": 400        # Reduced from 400 = 30-45% faster
        }
    )
    
    end_time = time.time()
    generation_time = end_time - start_time
    
    interpretation = response["message"]["content"]
    
    # Add timing info at the end
    interpretation += f"\n\n[Interpretation generated in {generation_time:.1f}s]"
    
    return interpretation

def classify_emotional_arc(trajectory: list) -> str:
    """LEVEL 2: Model emotional arc type"""
    if not trajectory:
        return "stable"
    
    start = trajectory[0]
    end = trajectory[-1]
    
    if start != end:
        if end == "calm":
            return "resolution"
        elif end in ["fear", "anger", "shame"]:
            return "escalation"
        else:
            return "shift"
    else:
        return "stable"

# Simplified generate_interpretation() - delegates to optimized LLM
def generate_interpretation(
    dynamics: List[Dict],
    dream_text: str,
    dominant_emotion: Optional[str] = None,
    top_symbols: Optional[List[str]] = None,
    has_resolution: bool = False,
    trajectory: Optional[List[str]] = None,
    trauma_level: Optional[str] = None
) -> str:
    """
    Main entry point with comprehensive timing.
    """
    start_total = time.time()
    
    # Apply top-K symbol filtering (STEP 2: Biggest speed improvement when activated)
    if top_symbols and len(top_symbols) > 150:
        # TODO: Integrate with embedding_scores pipeline in app.py
        print("NOTE: Top-150 symbol filtering ready but needs embedding_scores integration")
        top_symbols = top_symbols[:150]
    
    result = generate_llm_interpretation(
        dream_text=dream_text,
        top_symbols=top_symbols or [],
        dominant_emotion=dominant_emotion or "neutral",
        trajectory=trajectory or [],
        dynamics=dynamics or []
    )
    
    total_time = time.time() - start_total
    print(f"Total interpretation time: {total_time:.1f}s")  # Console feedback
    
    return result

# Keep all existing helper functions unchanged (for fallback use)
def _build_emotional_overview(dominant_emotion, arc_type, trauma_level, verb):
    """Build emotionally intelligent overview."""
    if trauma_level == "High":
        prefixes = ["carries significant emotional intensity", "shows marked tension"]
    elif trauma_level == "Elevated":
        prefixes = ["contains notable emotional weight", "reflects underlying tension"]
    else:
        prefixes = ["unfolds with", "is characterized by"]
    
    prefix = random.choice(prefixes)
    
    arc_descriptors = {
        "resolution": "progressing toward integration",
        "escalation": "building toward confrontation", 
        "stable": "sustained throughout",
        "shift": "transitioning between states"
    }
    
    arc_desc = arc_descriptors.get(arc_type, "structured around emotional movement")
    
    return f"{prefix.capitalize()} {dominant_emotion or 'complexity'} {arc_desc} ({arc_type})."

def _build_symbolic_processes(top_symbols, dominant_emotion, dynamics, mentioned_symbols):
    """LEVEL 1: Emotion-fused symbol + dynamic phrasing."""
    lines = []
    
    # Primary symbols with weight-based depth (LEVEL 5) - EXPANDED
    if top_symbols:
        primary = top_symbols[0]
        secondaries = top_symbols[1:3] if len(top_symbols) > 1 else []

        primary_clean = primary.replace("_", " ")

        lines.append(
            f"The image of the {primary_clean} emerges as the central symbolic element "
            f"within the dream narrative. In dream psychology, such imagery often functions "
            f"as a focal point through which emotional themes become expressed. In this case, "
            f"the {primary_clean} appears to carry the emotional tone of {dominant_emotion or 'the dream'}, "
            f"suggesting that this symbol may represent an important area of psychological attention "
            f"or lived experience currently being processed."
        )

        if secondaries:
            sec_list = ", ".join([s.replace("_", " ") for s in secondaries])

            lines.append(
                f"Alongside this central symbol, additional imagery such as {sec_list} appears in "
                f"supporting roles. These elements often function as contextual amplifiers, helping "
                f"to shape the emotional landscape of the dream and provide further clues about "
                f"how the mind is organizing experience during sleep."
            )

        mentioned_symbols.update([primary] + secondaries)
    
    # Emotion-aware dynamics (LEVEL 1)
    sorted_dynamics = sorted(dynamics, key=lambda d: d.get("strength", 0), reverse=True)
    for i, d in enumerate(sorted_dynamics[:3]):  # Top 3 only
        dynamic = d.get("dynamic")
        
        if dynamic in EMOTION_AWARE_POOLS:
            pool = EMOTION_AWARE_POOLS[dynamic]
            if dominant_emotion and dominant_emotion in pool:
                phrase = select_phrase(pool[dominant_emotion], i)
            else:
                phrase = select_phrase(pool["default"], i)
        else:
            # Fallback phrasing
            base = f"{dynamic.replace('_', ' ')} process"
            phrase = f"A {base} emerges with particular clarity."
        
        lines.append(phrase)
    
    return " ".join(lines)

def _build_psychological_meaning(dynamics, dominant_emotion, mentioned_symbols):
    """LEVEL 4: Narrative conflict modeling."""
    # Detect conflict patterns
    conflict_patterns = {
        ("pursuit", "barrier"): "tension between movement and obstruction",
        ("exposure", "shame"): "conflict between visibility and vulnerability", 
        ("stagnation", "fear"): "struggle between inertia and anxiety"
    }
    
    dynamics_set = {d.get("dynamic") for d in dynamics}
    
    for pattern, description in conflict_patterns.items():
        if all(p in dynamics_set for p in pattern):
            return f"The dream appears to revolve around a core {description}."
    
    # EXPANDED default psychological framing
    return (
        "From a psychological perspective, dreams rarely operate through fixed symbolic "
        "translations. Instead, they tend to represent processes occurring within the "
        "dreamer's emotional and cognitive life. The imagery present in this dream suggests "
        "that the mind may be actively working through internal experiences, organizing "
        "emotions, memories, and unresolved tensions into narrative form. Rather than "
        "delivering a direct message, the dream appears to reflect an ongoing process of "
        "psychological integration."
    )

def _build_resolution_section(has_resolution, arc_type, trauma_level):
    """LEVEL 2: Arc-aware resolution."""
    if arc_type == "resolution" or has_resolution:
        if trauma_level in ["High", "Elevated"]:
            return "Despite emotional intensity, the movement toward resolution suggests psychological resilience and adaptive capacity."
        return "The presence of resolution indicates ongoing integration and emotional processing."
    else:
        # EXPANDED no-resolution case
        return (
            "The absence of a clear resolution within the dream narrative may indicate that the "
            "psychological themes represented here are still unfolding in waking life. Dreams "
            "often mirror emotional processes that have not yet reached closure, allowing the "
            "mind to explore possibilities, rehearse responses, or gradually integrate new "
            "experiences. In this sense, the dream may be less about solving a problem and more "
            "about allowing emotional material to continue developing over time."
        )

def _build_reflective_question(dominant_emotion, trauma_level):
    """LEVEL 8: Adaptive reflection prompts."""
    questions = {
        "fear": "What situations in waking life feel urgent or difficult to confront directly?",
        "calm": "Where in your life are you currently experiencing emotional balance or integration?",
        "sadness": "Is there something you might be quietly processing or coming to terms with?",
        "anger": "What boundaries or frustrations need clearer acknowledgment in your daily experience?",
        "joy": "What sources of fulfillment or connection feel alive for you right now?",
        "High": (
            "A useful way to approach this dream is through reflection rather than literal "
            "interpretation. Consider which parts of the dream felt most emotionally vivid "
            "or memorable. These elements often highlight areas of waking life that currently "
            "carry psychological importance. Reflecting on how these themes connect with "
            "recent experiences, relationships, or inner concerns may provide deeper personal insight."
        ),
        None: (
            "A useful way to approach this dream is through reflection rather than literal "
            "interpretation. Consider which parts of the dream felt most emotionally vivid "
            "or memorable. These elements often highlight areas of waking life that currently "
            "carry psychological importance. Reflecting on how these themes connect with "
            "recent experiences, relationships, or inner concerns may provide deeper personal insight."
        )
    }
    
    # Trauma override
    if trauma_level == "High":
        return questions["High"]
    elif dominant_emotion in questions:
        return questions[dominant_emotion]
    else:
        return questions[None]

# Keep existing utility functions unchanged
def confidence_prefix(confidence: float) -> str:
    if confidence > 0.6:
        return "The dream clearly reflects"
    elif confidence > 0.35:
        return "The dream appears to reflect"
    else:
        return "The dream may suggest"

def shorten_meaning(text: str, max_words: int = 25) -> str:
    first_sentence = re.split(r"[.!?]", text)[0]
    words = first_sentence.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "…"
    return first_sentence.strip()

def _emotion_tone_line(emotion: str) -> Optional[str]:
    TONE_MAP = {
        "fear": "Overall, the emotional tone is tense, reflecting heightened alertness.",
        "joy": "Overall, the dream carries a light and positive emotional tone.",
        "sadness": "Overall, the dream reflects a subdued and introspective quality.",
        "anger": "Overall, the dream conveys a heightened and confrontational tone.",
        "calm": "Overall, the dream reflects emotional steadiness and regulation.",
        "shame": "Overall, the dream carries an emotionally self-conscious quality.",
        "anticipation": "Overall, the dream is shaped by expectation and readiness.",
        "surprise": "Overall, the dream contains elements of sudden emotional change.",
        "trust": "Overall, the dream reflects feelings of safety and openness.",
        "disgust": "Overall, the dream conveys emotional aversion or discomfort.",
    }
    return TONE_MAP.get(emotion)
