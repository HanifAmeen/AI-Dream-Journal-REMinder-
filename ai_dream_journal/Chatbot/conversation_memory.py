from collections import deque

class ConversationMemory:
    def __init__(self, max_turns=4):
        self.history = deque(maxlen=max_turns)

    def add_user(self, text):
        self.history.append(f"User: {text}")

    def add_bot(self, text):
        self.history.append(f"Bot: {text}")

    def render(self):
        return "\n".join(self.history)
