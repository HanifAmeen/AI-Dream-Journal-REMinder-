from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class DreamSimilarity:

    def __init__(self, model, dreambank_embeddings, dreambank_texts):
        self.model = model
        self.dreambank_embeddings = dreambank_embeddings
        self.dreambank_texts = dreambank_texts


    def find_similar_dreams(self, dream_text, top_k=3):

        user_embedding = self.model.encode([dream_text])

        similarities = cosine_similarity(
            user_embedding,
            self.dreambank_embeddings
        )[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []

        for idx in top_indices:
            score = float(similarities[idx]) * 100

            results.append({
                "dream_text": self.dreambank_texts[idx],
                "similarity_score": round(score, 2)
            })

        return results