import re

def detect_concrete_objects(dream_text: str, known_objects: set):
    """
    Detect concrete objects using word-boundary-safe regex.
    Handles plurals and punctuation.
    """
    text = dream_text.lower()
    found = set()

    for obj in known_objects:
        # Match singular or plural, with word boundaries
        pattern = rf"\b{re.escape(obj)}s?\b"
        if re.search(pattern, text):
            found.add(obj)

    return sorted(found)


def detect_literal_symbol_matches(dream_text, symbol_meaning_map):
    text = dream_text.lower()
    matches = {}

    for symbol, meaning in symbol_meaning_map.items():
        pattern = rf"\b{re.escape(symbol)}s?\b"
        if re.search(pattern, text):
            matches[symbol] = meaning

    return matches


def build_literal_symbol_notes(matches):
    if not matches:
        return ""

    lines = [
        "Related symbol references (descriptive sources):"
    ]

    for symbol, meaning in matches.items():
        lines.append(
            f"- **{symbol.capitalize()}** is commonly described as {meaning.lower()}."
        )

    return "\n".join(lines)
