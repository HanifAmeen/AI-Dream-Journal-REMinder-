EMOTION_KEYWORDS = {
    "fear": {"afraid", "scared", "terrified", "panic"},
    "anxiety": {"nervous", "uneasy", "worried"},
    "relief": {"relieved", "safe"},
    "sadness": {"sad", "crying"},
}

def detect_emotion(text: str) -> str | None:
    text = text.lower()
    for emotion, words in EMOTION_KEYWORDS.items():
        for w in words:
            if w in text:
                return emotion
    return None
