"""
Resume analysis.

A lightweight, explainable scoring engine. It has no ML model behind it
yet — every score is derived from transparent, rule-based signals so it's
easy to see exactly why a resume received the score it did. Swap the
internals for a real embedding/classification model later without
changing the response shape the frontend expects.
"""
from app.services.nlp_service import extract_skills
from app.services.matcher import calculate_similarity
from app.services.skill_gap import find_missing_skills
from app.services.ats import calculate_ats_score
from app.services.project_analyzer import analyze_projects
from app.services.semantic_matcher import semantic_similarity

from app.utils.constants import (
    SKILL_LIBRARY,
    SOFT_SKILL_NAMES,
    SECTION_KEYWORDS,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    YEARS_PATTERN,
    GROWTH_SKILLS,
    RECOMMENDATION_THRESHOLDS,
    RECOMMENDATION_FALLBACK,
)
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ScreeningResult:
    semantic_match: int
    project_score: int
    project_level: str
    project_count: int
    project_technologies: list[str]
    ats_score: int
    job_match: int
    skill_match: int
    confidence: int
    recommendation: str
    ats_breakdown: dict
    matching_skills: list[str]
    soft_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    weaknesses: list[str]
    detected_email: str | None = None
    detected_experience: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "semantic_match": self.semantic_match,
            "project_score": self.project_score,
            "project_level": self.project_level,
            "project_count": self.project_count,
            "project_technologies": self.project_technologies,
            "ats_score": self.ats_score,
            "ats_breakdown": self.ats_breakdown,
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


def _score_formatting(text: str, text_lower: str) -> tuple[int, list[str]]:
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


def analyze_resume(text: str, job_description: str | None = None) -> ScreeningResult:
    text_lower = text.lower()
    project_count = text_lower.count("project")
    project_info = analyze_projects(text)

    matched_skills = extract_skills(text)
    technical_skills = [s for s in matched_skills if s not in SOFT_SKILL_NAMES]
    soft_skills = [s for s in matched_skills if s in SOFT_SKILL_NAMES]

    total_technical_tracked = [s for s in SKILL_LIBRARY if s not in SOFT_SKILL_NAMES]
    skill_match = round(100 * len(technical_skills) / max(len(total_technical_tracked), 1))
    skill_match = min(skill_match * 3, 100)  # a handful of hits should already read as a strong match

    ats_score, warnings = _score_formatting(text, text_lower)

    if job_description:
     
    # TF-IDF similarity
     
     semantic_score = semantic_similarity(text, job_description)


    # Skill overlap
     jd_skills = extract_skills(job_description)

     if jd_skills:
        overlap = len(set(jd_skills) & set(technical_skills))
        skill_overlap = round(100 * overlap / len(jd_skills))
     else:
        skill_overlap = skill_match

    # Final Job Match
     job_match = round((skill_overlap * 0.6) + (semantic_score * 0.4))
    else:
        job_match = min(round(skill_match * 0.95), 100)
    ats = calculate_ats_score(
     skill_match=skill_match,
     job_match=job_match,
     formatting_score=ats_score,
     project_count=project_count,
     experience_years=experience_years,
    )
    confidence = round((ats_score * 0.4) + (skill_match * 0.35) + (job_match * 0.25))
    confidence = max(0, min(confidence, 100))

    recommendation = RECOMMENDATION_FALLBACK

    for threshold, label in RECOMMENDATION_THRESHOLDS:
     if confidence >= threshold:
        recommendation = label
        break

    if job_description:
        gap = find_missing_skills(text, job_description)
        missing_skills = gap["missing"]
    else:
    
        missing_skills = [s for s in GROWTH_SKILLS if s not in technical_skills]

    strengths = []
    if technical_skills:
        strengths.append(f"Demonstrated hands-on experience with {', '.join(technical_skills[:4])}.")
    if sum(1 for kw in SECTION_KEYWORDS if kw in text_lower) >= 3:
        strengths.append("Resume follows a clear, ATS-friendly structure.")
    if not strengths:
        strengths.append("Resume parsed successfully; add more detail for a fuller signal.")

    weaknesses = []
    if missing_skills:
        weaknesses.append(f"No mention of {', '.join(missing_skills)}.")
    if not soft_skills:
        weaknesses.append("No explicit soft-skill keywords detected.")
    if not weaknesses:
        weaknesses.append("No significant gaps detected against the tracked skill set.")

    email_match = EMAIL_PATTERN.search(text)
    years_match = YEARS_PATTERN.search(text)

    experience_years = 0

    if years_match:
      experience_years = int(years_match.group(1))

    return ScreeningResult(
        ats_score=ats.total,
        ats_breakdown={
          "skills": ats.skills,
          "job_match": ats.job_match,
          "formatting": ats.formatting,
          "projects": ats.projects,
          "experience": ats.experience,
        },
        semantic_match=semantic_score,
        project_score=project_info["project_score"],
        project_level=project_info["project_level"],
        project_count=project_info["project_count"],
        project_technologies=project_info["technologies"],
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
    )