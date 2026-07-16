"""
ATS Score Calculator
"""

from dataclasses import dataclass


@dataclass
class ATSBreakdown:
    skills: int
    job_match: int
    formatting: int
    projects: int
    experience: int
    total: int


def calculate_ats_score(
    skill_match: int,
    job_match: int,
    formatting_score: int,
    project_count: int,
    experience_years: int,
) -> ATSBreakdown:

    # Skills (35)
    skills_score = round((skill_match / 100) * 35)

    # Job Match (30)
    job_score = round((job_match / 100) * 30)

    # Formatting (15)
    formatting = round((formatting_score / 100) * 15)

    # Projects (10)
    if project_count >= 5:
        projects = 10
    elif project_count >= 3:
        projects = 8
    elif project_count >= 1:
        projects = 5
    else:
        projects = 0

    # Experience (10)
    if experience_years >= 5:
        experience = 10
    elif experience_years >= 3:
        experience = 8
    elif experience_years >= 1:
        experience = 5
    else:
        experience = 2

    total = (
        skills_score
        + job_score
        + formatting
        + projects
        + experience
    )

    return ATSBreakdown(
        skills=skills_score,
        job_match=job_score,
        formatting=formatting,
        projects=projects,
        experience=experience,
        total=min(total, 100),
    )