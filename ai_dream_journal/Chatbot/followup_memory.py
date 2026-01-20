class FollowUpMemory:
    def __init__(self):
        self.answers = {}

    def store(self, dream_id, question, answer):
        if dream_id not in self.answers:
            self.answers[dream_id] = []

        self.answers[dream_id].append({
            "question": question,
            "answer": answer
        })

    def get(self, dream_id):
        return self.answers.get(dream_id, [])
