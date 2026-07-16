from app.services.resume_ranker import (
    CandidateScore,
    rank_candidates,
    filter_by_skill,
)

candidates = [

    CandidateScore(
        filename="sayan.pdf",
        ats_score=92,
        job_match=95,
        semantic_match=94,
        project_score=90,
        recommendation="Highly Recommended",
        matching_skills=["Python", "FastAPI", "Docker"],
        missing_skills=[]
    ),

    CandidateScore(
        filename="dj.pdf",
        ats_score=85,
        job_match=82,
        semantic_match=81,
        project_score=84,
        recommendation="Recommended",
        matching_skills=["Python", "SQL"],
        missing_skills=["Docker"]
    ),

    CandidateScore(
        filename="mona.pdf",
        ats_score=70,
        job_match=68,
        semantic_match=66,
        project_score=72,
        recommendation="Worth a Look",
        matching_skills=["Java"],
        missing_skills=["Python"]
    ),

]

ranked = rank_candidates(candidates)

print("\n===== Ranking =====")

for c in ranked:
    print(
        c.rank,
        c.filename,
        c.overall_score,
    )

print("\n===== Python Candidates =====")

python_candidates = filter_by_skill(
    ranked,
    "Python"
)

for c in python_candidates:
    print(c.filename)