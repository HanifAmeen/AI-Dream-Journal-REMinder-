import random
from typing import Dict, List, Iterable
from nltk.corpus import wordnet as wn

# ------------------------------------------------------------------
# Sentence style templates
# ------------------------------------------------------------------

OPENERS = [
    "The presence of {obj} imagery",
    "{obj_cap} imagery",
    "Imagery involving {obj}",
    "The inclusion of {obj} imagery",
]

VERBS = [
    "contributes to",
    "adds to",
    "introduces",
    "helps establish",
    "plays a role in shaping",
]

QUALIFIERS = [
    "the overall atmosphere of the dream",
    "the emotional tone of the dream",
    "the background mood of the dream",
    "the dream’s general ambience",
]

SAFETY_CLAUSES = [
    "without imposing a fixed symbolic meaning",
    "without forcing a specific interpretation",
    "while remaining open to personal meaning",
    "without suggesting a definitive symbolic reading",
]

CONNECTORS = [
    "by evoking",
    "through associations with",
    "by drawing on",
    "through subtle references to",
]

# ------------------------------------------------------------------
# Linguistic normalization utilities
# ------------------------------------------------------------------

def is_noun(word: str) -> bool:
    """Check if WordNet recognises the word as a noun."""
    return bool(wn.synsets(word, pos=wn.NOUN))


def adjective_to_noun(word: str) -> str:
    """
    Convert adjectives or participles into grammatically safe noun forms.
    Uses WordNet first, then general English morphological fallbacks.
    """
    word = word.lower().strip()

    # Already a noun
    if is_noun(word):
        return word

    # WordNet derivational morphology
    for syn in wn.synsets(word, pos=wn.ADJ):
        for lemma in syn.lemmas():
            for related in lemma.derivationally_related_forms():
                if related.synset().pos() == "n":
                    return related.name().replace("_", " ")

    # Linguistic fallbacks (NOT hard-coded meanings)
    if word.endswith("en"):       # hidden → hiddenness
        return word + "ness"
    if word.endswith("e"):        # tense → tension
        return word[:-1] + "ion"

    return word + "ness"          # dark → darkness, calm → calmness


def normalize_descriptors(descriptors: List[str]) -> List[str]:
    """
    Normalize descriptors into guaranteed noun phrases.
    """
    return [adjective_to_noun(d) for d in descriptors if d]

# ------------------------------------------------------------------
# Sentence construction helpers
# ------------------------------------------------------------------

def _choose_descriptors(descriptors: List[str], max_items: int = 2) -> str:
    if not descriptors:
        return ""
    selected = random.sample(descriptors, min(max_items, len(descriptors)))
    return ", ".join(selected)


def _capitalize_object(obj: str) -> str:
    return obj.capitalize()


def _build_sentence(obj: str, descriptors: List[str]) -> str:
    opener = random.choice(OPENERS).format(
        obj=obj,
        obj_cap=_capitalize_object(obj)
    )

    verb = random.choice(VERBS)
    qualifier = random.choice(QUALIFIERS)
    safety = random.choice(SAFETY_CLAUSES)
    connector = random.choice(CONNECTORS)

    normalized = normalize_descriptors(descriptors)
    descriptor_text = _choose_descriptors(normalized)

    if descriptor_text:
        return (
            f"{opener} {verb} {qualifier} "
            f"{connector} {descriptor_text}, {safety}."
        )

    return f"{opener} {verb} {qualifier}, {safety}."

# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def build_descriptive_sentences(
    objects: Iterable[str],
    descriptive_map: Dict[str, List[str]]
) -> List[str]:
    """
    Build safe, non-interpretive descriptive sentences for concrete imagery.
    """
    sentences: List[str] = []

    for obj in objects:
        descriptors = descriptive_map.get(obj)
        if not descriptors:
            continue
        sentences.append(_build_sentence(obj, descriptors))

    return sentences
