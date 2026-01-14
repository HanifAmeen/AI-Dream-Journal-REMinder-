import csv
import re
from pathlib import Path

# --------------------------------------------------
# Robust CSV discovery (NO assumptions about folders)
# --------------------------------------------------

def find_csv_path(filename: str):
    """
    Walk upward from this file until we find:
    datasets/<filename>
    """
    current = Path(__file__).resolve()

    for parent in current.parents:
        candidate = parent / "datasets" / filename
        if candidate.exists():
            return candidate

    return None


CSV_PATH = find_csv_path("cleaned_dream_interpretations.csv")

# --------------------------------------------------
# Caches
# --------------------------------------------------
_DESCRIPTIVE_CACHE = None
_MEANING_CACHE = None

# --------------------------------------------------
# Language safety rules
# --------------------------------------------------
FORBIDDEN_PATTERNS = [
    r"unconscious",
    r"subconscious",
    r"masculine",
    r"feminine",
    r"represents",
    r"means",
    r"symbolizes",
    r"reflects your",
    r"message to the dreamer",
    r"inner self",
    r"desire",
    r"hidden meaning"
]

ALLOWED_DESCRIPTORS = {
    "fantasy",
    "stylized",
    "imaginative",
    "unreal",
    "exaggerated",
    "quiet",
    "independent",
    "observant",
    "mysterious",
    "vast",
    "hidden",
    "distant",
    "unknown",
    "calm",
    "gentle"
}


def _clean_text(text: str) -> str:
    text = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        text = re.sub(pattern, "", text)
    return text


# --------------------------------------------------
# Descriptive enrichment loader
# --------------------------------------------------
def load_descriptive_phrases():
    """
    Returns:
    {
        "cat": ["quiet", "independent"],
        "anime": ["fantasy", "stylized"]
    }
    """
    global _DESCRIPTIVE_CACHE

    if _DESCRIPTIVE_CACHE is not None:
        return _DESCRIPTIVE_CACHE

    mapping = {}

    if CSV_PATH is None:
        _DESCRIPTIVE_CACHE = mapping
        return mapping

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row.get("word", "").strip().lower()
            interpretation = row.get("interpretation", "")

            if not word or not interpretation:
                continue

            cleaned = _clean_text(interpretation)

            descriptors = [
                d for d in ALLOWED_DESCRIPTORS
                if d in cleaned
            ]

            # Keep word even if no descriptors match
            mapping[word] = sorted(set(descriptors))

    _DESCRIPTIVE_CACHE = mapping
    return mapping


# --------------------------------------------------
# Literal meaning reference loader
# --------------------------------------------------
def load_symbol_meanings():
    """
    Returns:
    {
        "cat": "...",
        "anime": "..."
    }
    """
    global _MEANING_CACHE

    if _MEANING_CACHE is not None:
        return _MEANING_CACHE

    meaning_map = {}

    if CSV_PATH is None:
        _MEANING_CACHE = meaning_map
        return meaning_map

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row.get("word", "").strip().lower()
            interpretation = row.get("interpretation", "").strip()

            if not word or not interpretation:
                continue

            meaning_map[word] = interpretation

    _MEANING_CACHE = meaning_map
    return meaning_map


# --------------------------------------------------
# DIRECT TEST MODE (THIS IS THE KEY)
# --------------------------------------------------
if __name__ == "__main__":
    print("=== CSV LOAD TEST ===")
    print("Resolved CSV_PATH:", CSV_PATH)
    print("CSV exists:", CSV_PATH is not None)

    desc = load_descriptive_phrases()
    meanings = load_symbol_meanings()

    print("\nTotal descriptive entries:", len(desc))
    print("Total meaning entries:", len(meanings))

    print("\nSample descriptive keys:", list(desc.keys())[:10])
    print("Sample meaning keys:", list(meanings.keys())[:10])

    for test_word in ["cat", "anime", "forest", "forrest"]:
        print(
            f"\nContains '{test_word}':",
            test_word in meanings,
            "| descriptors:",
            desc.get(test_word)
        )
