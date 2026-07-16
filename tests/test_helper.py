from app.utils import helper
from app.utils.constants import (
    RECOMMENDATION_FALLBACK,
    RECOMMENDATION_THRESHOLDS,
    SKILL_LIBRARY,
    SOFT_SKILL_NAMES,
)


def test_screening_result_to_dict_contains_all_fields():
    result = helper.ScreeningResult(
        ats_score=80,
        job_match=70,
        skill_match=60,
        confidence=75,
        recommendation="Shortlist",
        matching_skills=["Python"],
        soft_skills=["Communication"],
        missing_skills=["Docker"],
        strengths=["Strong Python skills"],
        weaknesses=["Add Docker"],
        detected_email="test@example.com",
        detected_experience="5 Years",
        warnings=[],
        section_data={"skills": "Python"},
        missing_sections=["Projects"],
        section_statistics={"skills": 1},
    )

    data = result.to_dict()

    assert data["ats_score"] == 80
    assert data["detected_email"] == "test@example.com"
    assert data["section_data"] == {"skills": "Python"}
    assert data["missing_sections"] == ["Projects"]


def test_find_skills_detects_known_skill():
    skill, variants = next(iter(SKILL_LIBRARY.items()))

    found = helper.find_skills(f"I have worked with {variants[0]}.")

    assert skill in found


def test_score_formatting_covers_short_normal_and_long_resumes():
    short_score, short_warnings = helper.score_formatting(
        "Short resume",
        "short resume",
    )
    assert short_score >= 40
    assert any("No email address" in warning for warning in short_warnings)
    assert any("No phone number" in warning for warning in short_warnings)
    assert any("very short" in warning for warning in short_warnings)

    normal_text = "test@example.com 9876543210 " + ("detail " * 150)
    normal_score, normal_warnings = helper.score_formatting(
        normal_text,
        normal_text.lower(),
    )
    assert normal_score > 40
    assert not any("very short" in warning for warning in normal_warnings)
    assert not any("unusually long" in warning for warning in normal_warnings)

    long_text = "test@example.com 9876543210 " + ("detail " * 1300)
    _, long_warnings = helper.score_formatting(
        long_text,
        long_text.lower(),
    )
    assert any("unusually long" in warning for warning in long_warnings)


def test_score_job_match_covers_all_branches():
    assert helper.score_job_match("", [], 80, None) == 76

    skill, variants = next(iter(SKILL_LIBRARY.items()))
    jd_skills = helper.find_skills(variants[0])

    score_with_skills = helper.score_job_match(
        "",
        jd_skills,
        0,
        variants[0],
    )
    assert score_with_skills == 100

    fallback_score = helper.score_job_match(
        "puzzletree rocketship",
        [],
        0,
        "puzzletree sailboat",
    )
    assert fallback_score == 50


def test_recommendation_for_uses_thresholds_and_fallback():
    for threshold, label in RECOMMENDATION_THRESHOLDS:
        assert helper.recommendation_for(threshold) == label

    assert helper.recommendation_for(-1) == RECOMMENDATION_FALLBACK


def test_analyze_resume_returns_strong_profile(monkeypatch):
    technical_skill = next(
        skill for skill in SKILL_LIBRARY
        if skill not in SOFT_SKILL_NAMES
    )
    soft_skill = next(iter(SOFT_SKILL_NAMES))

    monkeypatch.setattr(
        helper,
        "extract_sections",
        lambda text: {
            "summary": "Summary",
            "skills": "Skills",
            "experience": "Experience",
            "education": "Education",
            "projects": "Projects",
        },
    )
    monkeypatch.setattr(helper, "missing_sections", lambda text: [])
    monkeypatch.setattr(
        helper,
        "section_statistics",
        lambda text: {"total_sections": 5},
    )

    text = (
        f"test@example.com 9876543210 "
        f"{SKILL_LIBRARY[technical_skill][0]} "
        f"{SKILL_LIBRARY[soft_skill][0]} "
        "5 years of experience "
        + ("detail " * 150)
    )

    result = helper.analyze_resume(text)

    assert technical_skill in result.matching_skills
    assert soft_skill in result.soft_skills
    assert result.detected_email == "test@example.com"
    assert result.detected_experience == "5 Years"
    assert result.section_data["summary"] == "Summary"
    assert result.section_statistics["total_sections"] == 5
    assert any("well-defined ATS sections" in item for item in result.strengths)


def test_analyze_resume_returns_gaps_for_weak_profile(monkeypatch):
    monkeypatch.setattr(helper, "extract_sections", lambda text: {})
    monkeypatch.setattr(
        helper,
        "missing_sections",
        lambda text: ["Education", "Projects"],
    )
    monkeypatch.setattr(
        helper,
        "section_statistics",
        lambda text: {"total_sections": 0},
    )

    result = helper.analyze_resume("brief resume")

    assert result.matching_skills == ["No tracked skills detected"]
    assert result.missing_sections == ["Education", "Projects"]
    assert any("Missing resume sections" in item for item in result.weaknesses)
    assert "No explicit soft-skill keywords detected." in result.weaknesses