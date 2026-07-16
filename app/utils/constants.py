"""
Static config for resume analysis: the skill library, section keywords,
and regex patterns. No logic here — just the data helper.py scores against.
"""

import re

# Canonical skill -> the substrings we'll look for in the resume text
# (all matched case-insensitively against normalized text).
SKILL_LIBRARY: dict[str, list[str]] = {
    "Python": ["python"],
    "SQL": ["sql", "postgresql", "mysql"],
    "FastAPI": ["fastapi"],
    "Docker": ["docker"],
    "AWS": ["aws", "amazon web services"],
    "TensorFlow": ["tensorflow"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "NLP": ["nlp", "natural language processing"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Kubernetes": ["kubernetes", "k8s"],
    "MLOps": ["mlops", "ml ops"],
    "System Design": ["system design"],
    "React": ["react.js", "react"],
    "JavaScript": ["javascript", "js"],
    "Git": ["git", "github"],
    "Machine Learning": ["machine learning"],
    "Deep Learning": ["deep learning"],
    "REST APIs": ["rest api", "restful"],
    "Communication": ["communication"],
    "Leadership": ["leadership", "led a team", "team lead"],
    "Problem Solving": ["problem solving", "problem-solving"],
}

# Skills classified as "soft" rather than technical — used to split
# matching_skills vs soft_skills in the response.
SOFT_SKILL_NAMES = {"Communication", "Leadership", "Problem Solving"}

# Skills we specifically flag as "missing" when absent, since they're
# common gaps for junior/mid candidates and useful growth signals.
GROWTH_SKILLS = ("Kubernetes", "MLOps", "System Design")

# Resume section headers an ATS-friendly resume is expected to have.
SECTION_KEYWORDS = ["experience", "education", "skills", "projects", "summary"]

# Contact / experience detection.
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s\-().]{8,}\d)")
YEARS_PATTERN = re.compile(r"(\d+)\+?\s*(?:years|yrs)", re.IGNORECASE)

# Upload constraints.
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB, matches the "up to 10MB" hint in the UI

# Recommendation tiers by confidence score.
RECOMMENDATION_THRESHOLDS = (
    (85, "Highly Recommended"),
    (70, "Recommended"),
    (50, "Worth a Look"),
)
RECOMMENDATION_FALLBACK = "Not a Strong Fit"