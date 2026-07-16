import spacy
from spacy.matcher import PhraseMatcher

from app.utils.constants import SKILL_LIBRARY

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# Create PhraseMatcher
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

# Add every keyword as a pattern for its canonical skill
for skill_name, keywords in SKILL_LIBRARY.items():
    patterns = [nlp.make_doc(keyword) for keyword in keywords]
    matcher.add(skill_name, patterns)


def extract_skills(text: str) -> list[str]:
    """Extract canonical skills from resume text."""

    doc = nlp(text)

    matches = matcher(doc)

    detected = set()

    for match_id, start, end in matches:
        skill = nlp.vocab.strings[match_id]
        detected.add(skill)

    return sorted(detected)