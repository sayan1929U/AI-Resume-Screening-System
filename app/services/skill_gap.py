"""
Compare resume skills with job description skills.
"""

from app.services.nlp_service import extract_skills


def find_missing_skills(resume_text: str, job_description: str):
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(job_description))

    matching = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)

    return {
        "matching": matching,
        "missing": missing
    }