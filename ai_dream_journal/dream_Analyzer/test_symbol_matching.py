import sys
from pathlib import Path
import re

# -------------------------------------------------
# Add analyzer directory to Python path
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# -------------------------------------------------
# Import project modules
# -------------------------------------------------
from symbol_insight import build_symbol_insight
from confidence_utils import compute_symbol_confidence


# -------------------------------------------------
# Test Dreams
# -------------------------------------------------
test_dreams = [
    """ I had a dream that I was walking through an old abandoned house late at night. The hallway was very quiet and the lights were flickering on and off. As I walked deeper into the house I heard footsteps behind me, but every time I turned around no one was there.

Suddenly I opened a door and found a staircase leading down into a dark basement. When I reached the bottom I saw a large mirror on the wall. When I looked into the mirror my reflection didn’t move the same way I did, and it slowly started smiling at me."""
]


# -------------------------------------------------
# Basic Symbol Extraction
# -------------------------------------------------
IGNORE_WORDS = {
    "i","was","a","the","and","in","of","it","that",
    "through","me","front","large","walking","appeared",
    "suddenly","while","above","below","being"
}


def extract_candidate_symbols(text):

    tokens = word_tokenize(text.lower())
    tagged = pos_tag(tokens)

    symbols = []

    for word, tag in tagged:

        # keep nouns only
        if tag.startswith("NN") and len(word) > 2:
            symbols.append(word)

    # remove duplicates but keep order
    return list(dict.fromkeys(symbols))


# -------------------------------------------------
# Run Symbol Tests
# -------------------------------------------------
for i, dream in enumerate(test_dreams, 1):

    print("\n" + "="*60)
    print(f"TEST DREAM {i}")
    print("="*60)

    print("\nDream Text:")
    print(dream)

    # ---------------------------------------------
    # Extract candidate symbols
    # ---------------------------------------------
    symbols = extract_candidate_symbols(dream)

    print("\nExtracted Candidate Symbols:")
    print(symbols)

    # ---------------------------------------------
    # Create symbol score dictionary
    # ---------------------------------------------
    symbol_scores = {symbol: 1.0 for symbol in symbols}

    # ---------------------------------------------
    # Compute symbol confidence
    # ---------------------------------------------
    confidence_score = compute_symbol_confidence(symbol_scores, dream)

    print("\nSymbol Confidence Score:")
    print(confidence_score)

    # ---------------------------------------------
    # Generate symbol insights
    # ---------------------------------------------
    print("\nSymbol Insights:")

    dominant_emotion = "neutral"

    insights = build_symbol_insight(
        symbol_scores,
        dominant_emotion,
        dream
    )

    print(insights)