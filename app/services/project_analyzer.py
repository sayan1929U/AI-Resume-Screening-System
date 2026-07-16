"""
Analyze resume projects and assign a quality score.
"""

import re

PROJECT_KEYWORDS = [
    "project",
    "experience",
]

TECH_FEATURES = {
    "FastAPI": 8,
    "Flask": 6,
    "Django": 8,
    "Docker": 10,
    "Kubernetes": 10,
    "AWS": 10,
    "Azure": 10,
    "GCP": 10,
    "Redis": 8,
    "PostgreSQL": 8,
    "MongoDB": 7,
    "MySQL": 6,
    "TensorFlow": 10,
    "PyTorch": 10,
    "Scikit-learn": 8,
    "LangChain": 10,
    "RAG": 10,
    "LLM": 10,
    "OpenAI": 10,
    "Git": 5,
    "GitHub": 5,
    "CI/CD": 8,
    "REST API": 6,
    "Authentication": 6,
}


def analyze_projects(text: str):
    text_lower = text.lower()

    score = 0

    detected = []

    for tech, weight in TECH_FEATURES.items():
        if tech.lower() in text_lower:
            score += weight
            detected.append(tech)

    score = min(score, 100)

    if score >= 90:
        level = "Excellent"
    elif score >= 75:
        level = "Advanced"
    elif score >= 55:
        level = "Intermediate"
    else:
        level = "Basic"

    project_count = len(
        re.findall(
            r"project",
            text_lower
        )
    )

    return {
        "project_score": score,
        "project_level": level,
        "project_count": project_count,
        "technologies": detected,
    }