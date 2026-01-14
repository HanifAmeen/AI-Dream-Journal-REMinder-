# interpretation_generator.py
import re
from typing import List, Dict, Optional

from phrasing_pools import PHRASING_POOLS
from phrase_selector import select_phrase

from symbols.descriptive_csv_loader import (
    load_descriptive_phrases,
    load_symbol_meanings
)
from symbols.concrete_object_detector import detect_concrete_objects
from symbols.descriptive_enrichment import build_descriptive_sentences


def generate_interpretation(
    dynamics: List[Dict],
    dream_text: str,
    dominant_emotion: Optional[str] = None
) -> str:
    """
    Generate a human-readable interpretation from resolved dynamics
    using controlled phrasing pools, with optional descriptive enrichment
    and factual symbol grounding.
    """
    paragraphs = []

    # ------------------------------------------------
    # Load CSV resources ONCE
    # ------------------------------------------------
    descriptive_map = load_descriptive_phrases()
    symbol_meanings = load_symbol_meanings()

    # Detect concrete objects from known symbols
    known_objects = set(symbol_meanings.keys())
    objects = detect_concrete_objects(dream_text, known_objects)

    # ------------------------------------------------
    # Core symbolic interpretation
    # ------------------------------------------------
    if not dynamics:
        if objects:
            paragraphs.append(
                "The dream is primarily composed of concrete, situational imagery and does not "
                "indicate a strong symbolic conflict or heightened psychological tension."
            )
        else:
            paragraphs.append(
                "The dream does not strongly activate a specific symbolic pattern, suggesting "
                "a diffuse or unresolved emotional experience."
            )
    else:
        for i, d in enumerate(dynamics):
            dynamic = d.get("dynamic")

            if dynamic in PHRASING_POOLS:
                phrase = select_phrase(PHRASING_POOLS[dynamic], i)
                paragraphs.append(phrase)
            else:
                paragraphs.append(
                    f"The dream highlights a symbolic dynamic related to "
                    f"{dynamic.replace('_', ' ')}, without assigning a fixed interpretation."
                )

    # ------------------------------------------------
    # Descriptive enrichment (contextual, non-interpretive)
    # ------------------------------------------------
    if objects:
        descriptive_sentences = build_descriptive_sentences(objects, descriptive_map)
        paragraphs.extend(descriptive_sentences)

    # ------------------------------------------------
    # Literal CSV symbol references (factual grounding)
    # ------------------------------------------------
    if objects:
        ref_lines = ["Related symbol references (from descriptive sources):"]
        for obj in objects:
            meaning = symbol_meanings.get(obj)
            if meaning:
                short = shorten_meaning(meaning.lower())
                ref_lines.append(
                    f"- {obj.capitalize()} is commonly described as {short}."
                )

        if len(ref_lines) > 1:
            paragraphs.append("\n".join(ref_lines))

    # ------------------------------------------------
    # Optional emotional tone line
    # ------------------------------------------------
    if dominant_emotion:
        tone_line = _emotion_tone_line(dominant_emotion)
        if tone_line:
            paragraphs.append(tone_line)

    return "\n\n".join(paragraphs)


def confidence_prefix(confidence: float) -> str:
    """Generate confidence-based phrasing."""
    if confidence > 0.6:
        return "The dream clearly reflects"
    elif confidence > 0.35:
        return "The dream appears to reflect"
    else:
        return "The dream may suggest"


def shorten_meaning(text: str, max_words: int = 25) -> str:
    """
    Reduce a long CSV meaning to a concise, neutral sentence.
    """
    first_sentence = re.split(r"[.!?]", text)[0]
    words = first_sentence.split()

    if len(words) > max_words:
        return " ".join(words[:max_words]) + "…"
    return first_sentence.strip()


def _emotion_tone_line(emotion: str) -> Optional[str]:
    """
    Append a single tone-setting line based on dominant emotion.
    """
    TONE_MAP = {
        "fear": (
            "Overall, the emotional tone of the dream is tense, "
            "reflecting heightened alertness or concern."
        ),
        "joy": (
            "Overall, the dream carries a light and positive emotional tone."
        ),
        "sadness": (
            "Overall, the dream reflects a subdued and introspective emotional quality."
        ),
        "anger": (
            "Overall, the dream conveys a heightened and confrontational emotional tone."
        ),
        "calm": (
            "Overall, the dream reflects a sense of emotional steadiness and regulation."
        ),
        "shame": (
            "Overall, the dream carries an emotionally self-conscious or exposed quality."
        ),
        "anticipation": (
            "Overall, the dream is shaped by a sense of expectation or emotional readiness."
        ),
        "surprise": (
            "Overall, the dream contains elements of sudden change or emotional disruption."
        ),
        "trust": (
            "Overall, the dream reflects feelings of safety or emotional openness."
        ),
        "disgust": (
            "Overall, the dream conveys a sense of emotional aversion or discomfort."
        ),
    }

    return TONE_MAP.get(emotion)
