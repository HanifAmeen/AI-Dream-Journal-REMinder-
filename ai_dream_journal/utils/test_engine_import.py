from ai_dream_journal.utils.interpretations_engine import (
    load_dreambank,
    build_tfidf,
    build_topics,
    vectorize_new_dream,
    detect_tension,
    get_topic_keywords,
    get_dominant_topics,
    generate_interpretation,
)



# Load dataset
df = load_dreambank()
texts = df["text"].tolist()

# Train TF-IDF
vectorizer, X = build_tfidf(texts)

# Train topic model
topic_model, W, H = build_topics(X, n_topics=8)

# Inspect topics (IMPORTANT)
topic_keywords = get_topic_keywords(topic_model, vectorizer)
print("Learned Topics:")
for k, v in topic_keywords.items():
    print(f"Topic {k}: {v}")


dream_text = (
    "I was walking across a narrow bridge at night. "
    "Fog surrounded me and I could not see what was ahead, "
    "but I kept moving forward."
)

tfidf_vec, topic_dist = vectorize_new_dream(
    dream_text, vectorizer, topic_model
)

print("Topic distribution:", topic_dist)

dominant_topics = get_dominant_topics(topic_dist, threshold=0.15)
print("Dominant topics:", dominant_topics)

tension = detect_tension(topic_dist)
print("Tension type:", tension)


keywords = []
for t in dominant_topics:
    keywords.extend(topic_keywords[t])

keywords = list(dict.fromkeys(keywords))  # deduplicate

interpretation = generate_interpretation(keywords, tension)
print("\nINTERPRETATION:")
print(interpretation)
