from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load once when the server starts
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(resume_text: str, job_description: str) -> int:
    """
    Returns semantic similarity score (0-100)
    """

    if not resume_text.strip():
        return 0

    if not job_description.strip():
        return 0

    embeddings = model.encode(
        [resume_text, job_description],
        convert_to_numpy=True,
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return round(similarity * 100)