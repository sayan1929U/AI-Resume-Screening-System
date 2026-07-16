from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CandidateScore:
    filename: str
    ats_score: int
    job_match: int
    recommendation: str

    
    semantic_match: int = 0
    project_score: int = 0

    

    matching_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)

    overall_score: float = 0.0
    rank: int = 0


def calculate_overall_score(candidate: CandidateScore) -> float:
    """
    Overall recruiter score.
    """

    score = (
        candidate.ats_score * 0.30
        + candidate.job_match * 0.30
        + candidate.semantic_match * 0.25
        + candidate.project_score * 0.15
    )

    return round(score, 2)


def rank_candidates(
    candidates: list[CandidateScore],
) -> list[CandidateScore]:

    for candidate in candidates:
        candidate.overall_score = calculate_overall_score(candidate)

    candidates.sort(
        key=lambda x: x.overall_score,
        reverse=True,
    )

    for i, candidate in enumerate(candidates, start=1):
        candidate.rank = i

    return candidates


def filter_by_skill(
    candidates: list[CandidateScore],
    skill: str,
) -> list[CandidateScore]:

    skill = skill.lower()

    return [
        c
        for c in candidates
        if skill in [s.lower() for s in c.matching_skills]
    ]