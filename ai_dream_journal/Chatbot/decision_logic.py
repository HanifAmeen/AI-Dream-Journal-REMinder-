def should_ask_question(dream_text, symbols, dominant_emotion):
    word_count = len(dream_text.split())
    symbol_count = len(symbols)

    # Short or vague dreams → ask clarifying question
    if word_count < 60:
        return True

    # High anxiety often benefits from reflection
    if dominant_emotion in {"anxiety", "fear"} and symbol_count <= 2:
        return True

    # Otherwise, offer insight
    return False
