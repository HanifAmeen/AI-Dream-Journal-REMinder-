def home_prompt(user_message):
    return f"""
User asked: {user_message}

Respond with a short, grounded explanation about dreams.
Do NOT analyze the user personally.
Encourage curiosity, not interpretation.
"""


def input_prompt(dream_text):
    return f"""
Dream text:
{dream_text}

Ask ONE clarifying question that would improve psychological interpretation.
Do not interpret yet.
"""


def analysis_prompt(dream_text, symbols, dominant_emotion):
    return f"""
Dream:
{dream_text}

Detected symbols: {symbols}
Dominant emotion: {dominant_emotion}

Provide one additional insight OR ask one reflective follow-up question.
Avoid repeating the main analysis.
"""
