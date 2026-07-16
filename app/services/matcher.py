from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess(text: str) -> str:
    return " ".join(text.lower().split())


def calculate_similarity(resume_text: str, job_description: str) -> int:
    resume_text = preprocess(resume_text)
    job_description = preprocess(job_description)

    if not resume_text or not job_description:
        return 0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
    )

    tfidf = vectorizer.fit_transform([resume_text, job_description])

    similarity = cosine_similarity(tfidf[0], tfidf[1])[0][0]

    return round(similarity * 100)