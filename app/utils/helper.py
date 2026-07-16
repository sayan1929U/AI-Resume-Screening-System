"""
Resume scoring logic.

A lightweight, explainable engine — no ML model behind it yet, every
score is derived from transparent rule-based signals so it's easy to see
exactly why a resume received the score it did. Swap the internals for a
real embedding/classification model later without changing the response
shape upload.py returns to the frontend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from app.services.section_detector import (
    extract_sections,
    missing_sections,
    section_statistics,
)

from app.utils.constants import (
    EMAIL_PATTERN,
    GROWTH_SKILLS,
    PHONE_PATTERN,
    RECOMMENDATION_FALLBACK,
    RECOMMENDATION_THRESHOLDS,
    SECTION_KEYWORDS,
    SKILL_LIBRARY,
    SOFT_SKILL_NAMES,
    YEARS_PATTERN,
)


@dataclass
class ScreeningResult:
    ats_score: int
    job_match: int
    skill_match: int
    confidence: int
    recommendation: str
    matching_skills: list[str]
    soft_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    weaknesses: list[str]
    detected_email: str | None = None
    detected_experience: str | None = None
    warnings: list[str] = field(default_factory=list)
    section_data: dict = field(default_factory=dict)
    missing_sections: list[str] = field(default_factory=list)
    section_statistics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "section_data": self.section_data,
            "missing_sections": self.missing_sections,
            "section_statistics": self.section_statistics,
            "ats_score": self.ats_score,
            "job_match": self.job_match,
            "skill_match": self.skill_match,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "matching_skills": self.matching_skills,
            "soft_skills": self.soft_skills,
            "missing_skills": self.missing_skills,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "detected_email": self.detected_email,
            "detected_experience": self.detected_experience,
            "warnings": self.warnings,
        }


def find_skills(text_lower: str) -> list[str]:
    """Return every SKILL_LIBRARY entry whose keyword variants appear in the text."""
    found = []
    for skill, variants in SKILL_LIBRARY.items():
        if any(variant in text_lower for variant in variants):
            found.append(skill)
    return found


def score_formatting(text: str, text_lower: str) -> tuple[int, list[str]]:
    """Simple ATS-compatibility heuristic based on structure, not looks."""
    warnings = []
    score = 40  # base score for a file that parsed at all

    sections_present = sum(1 for kw in SECTION_KEYWORDS if kw in text_lower)
    score += sections_present * 8  # up to +40

    if EMAIL_PATTERN.search(text):
        score += 5
    else:
        warnings.append("No email address detected — recruiters may not be able to reach this candidate.")

    if PHONE_PATTERN.search(text):
        score += 5
    else:
        warnings.append("No phone number detected.")

    word_count = len(text.split())
    if word_count < 120:
        warnings.append("Resume looks very short — may be missing detail an ATS can score.")
    elif word_count > 1200:
        warnings.append("Resume is unusually long — consider tightening it for readability.")
    else:
        score += 10

    return min(score, 100), warnings


def score_job_match(text_lower: str, technical_skills: list[str], skill_match: int, job_description: str | None) -> int:
    """How well the resume lines up with a job description, if one was supplied."""
    if not job_description:
        # no JD supplied — approximate using overall skill coverage
        return min(round(skill_match * 0.95), 100)

    jd_lower = job_description.lower()
    jd_skills = find_skills(jd_lower)

    if jd_skills:
        overlap = len(set(jd_skills) & set(technical_skills))
        return round(100 * overlap / len(jd_skills))

    # no recognizable skills in the JD text — fall back to loose keyword overlap
    jd_words = set(re.findall(r"[a-zA-Z]{4,}", jd_lower))
    resume_words = set(re.findall(r"[a-zA-Z]{4,}", text_lower))
    return round(100 * len(jd_words & resume_words) / max(len(jd_words), 1))


def recommendation_for(confidence: int) -> str:
    for threshold, label in RECOMMENDATION_THRESHOLDS:
        if confidence >= threshold:
            return label
    return RECOMMENDATION_FALLBACK


def analyze_resume(text: str, job_description: str | None = None) -> ScreeningResult:
    text_lower = text.lower()
    # Detect resume sections
    sections = extract_sections(text)
    missing_sections_list = missing_sections(text)
    section_stats = section_statistics(text)

    matched_skills = find_skills(text_lower)
    technical_skills = [s for s in matched_skills if s not in SOFT_SKILL_NAMES]
    soft_skills = [s for s in matched_skills if s in SOFT_SKILL_NAMES]

    total_technical_tracked = [s for s in SKILL_LIBRARY if s not in SOFT_SKILL_NAMES]
    skill_match = round(100 * len(technical_skills) / max(len(total_technical_tracked), 1))
    skill_match = min(skill_match * 3, 100)  # a handful of hits should already read as a strong match

    ats_score, warnings = score_formatting(text, text_lower)
    job_match = score_job_match(text_lower, technical_skills, skill_match, job_description)

    confidence = round((ats_score * 0.4) + (skill_match * 0.35) + (job_match * 0.25))
    confidence = max(0, min(confidence, 100))
    recommendation = recommendation_for(confidence)

    missing_skills = [s for s in GROWTH_SKILLS if s not in technical_skills]

    strengths = []
    if technical_skills:
        strengths.append(f"Demonstrated hands-on experience with {', '.join(technical_skills[:4])}.")
    if len(sections) >= 5:
        strengths.append(
        f"Resume contains {len(sections)} well-defined ATS sections." )
    if not strengths:
        strengths.append("Resume parsed successfully; add more detail for a fuller signal.")

    weaknesses = []
    if missing_sections_list:
     weaknesses.append(
        "Missing resume sections: "
        + ", ".join(missing_sections_list[:4])
        )
    if not soft_skills:
        weaknesses.append("No explicit soft-skill keywords detected.")
    if not weaknesses:
        weaknesses.append("No significant gaps detected against the tracked skill set.")

    email_match = EMAIL_PATTERN.search(text)
    years_match = YEARS_PATTERN.search(text)

    return ScreeningResult(
        ats_score=ats_score,
        job_match=job_match,
        skill_match=skill_match,
        confidence=confidence,
        recommendation=recommendation,
        matching_skills=technical_skills[:8] or ["No tracked skills detected"],
        soft_skills=soft_skills,
        missing_skills=missing_skills,
        strengths=strengths,
        weaknesses=weaknesses,
        detected_email=email_match.group(0) if email_match else None,
        detected_experience=f"{years_match.group(1)} Years" if years_match else None,
        warnings=warnings,
        section_data=sections,
        missing_sections=missing_sections_list,
        section_statistics=section_stats,
    )