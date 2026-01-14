import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import numpy as np

def load_dreambank(path="datasets/dreambank.csv"):
    df = pd.read_csv(path)
    df = df[["number", "report"]].dropna()
    df.rename(columns={"number": "dream_id", "report": "text"}, inplace=True)
    return df

def build_tfidf(corpus):
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_df=0.85,
        min_df=5,
        ngram_range=(1,2)
    )
    X = vectorizer.fit_transform(corpus)
    return vectorizer, X

def build_topics(tfidf_matrix, n_topics=10):
    model = NMF(n_components=n_topics, random_state=42)
    W = model.fit_transform(tfidf_matrix)
    H = model.components_
    return model, W, H

def vectorize_new_dream(text, vectorizer, topic_model):
    tfidf = vectorizer.transform([text])
    topic_distribution = topic_model.transform(tfidf)
    return tfidf, topic_distribution


def detect_tension(topic_distribution):
    sorted_topics = np.sort(topic_distribution[0])[::-1]
    if len(sorted_topics) >= 2 and abs(sorted_topics[0] - sorted_topics[1]) < 0.05:
        return "competing themes"
    return "dominant theme"

def get_topic_keywords(model, vectorizer, top_n=10):
    feature_names = vectorizer.get_feature_names_out()
    topics = {}
    for idx, topic in enumerate(model.components_):
        top_features = [feature_names[i] for i in topic.argsort()[-top_n:]]
        topics[idx] = top_features
    return topics
def get_dominant_topics(topic_distribution, threshold=0.15):
    return [
        i for i, weight in enumerate(topic_distribution[0])
        if weight > threshold
    ]
def generate_interpretation(topic_keywords, tension_type):
    if tension_type == "competing themes":
        return (
            f"The dream engages multiple psychological themes, particularly "
            f"{', '.join(topic_keywords[:5])}. These themes coexist without resolution, "
            f"creating sustained internal tension."
        )
