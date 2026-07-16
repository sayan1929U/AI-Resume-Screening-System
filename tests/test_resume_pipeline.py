import pytest
from fastapi import HTTPException

from app.services import resume_pipeline


def test_pipeline_rejects_unsupported_file_type():
    with pytest.raises(HTTPException) as error:
        resume_pipeline.analyze_uploaded_resume(
            filename="resume.txt",
            file_bytes=b"some text",
        )

    assert error.value.status_code == 400


def test_pipeline_rejects_empty_file():
    with pytest.raises(HTTPException) as error:
        resume_pipeline.analyze_uploaded_resume(
            filename="resume.pdf",
            file_bytes=b"",
        )

    assert error.value.status_code == 400
    assert error.value.detail == "The uploaded file is empty."


def test_pipeline_returns_analysis(monkeypatch):
    class FakeAnalysis:
        def to_dict(self):
            return {
                "ats_score": 90,
                "overall_score": 88.5,
            }

    monkeypatch.setattr(
        resume_pipeline,
        "extract_text",
        lambda filename, file_bytes: "Python developer with FastAPI experience",
    )
    monkeypatch.setattr(
        resume_pipeline,
        "analyze_resume",
        lambda text, job_description: FakeAnalysis(),
    )

    result = resume_pipeline.analyze_uploaded_resume(
        filename="candidate.pdf",
        file_bytes=b"fake PDF content",
        candidate_name="Asha",
        role="Backend Developer",
        job_description="Python and FastAPI",
    )

    assert result["message"] == "Resume analyzed successfully."
    assert result["filename"] == "candidate.pdf"
    assert result["candidate_name"] == "Asha"
    assert result["role"] == "Backend Developer"
    assert result["ats_score"] == 90


def test_pipeline_returns_422_when_file_cannot_be_read(monkeypatch):
    def raise_read_error(filename, file_bytes):
        raise ValueError("corrupted file")

    monkeypatch.setattr(resume_pipeline, "extract_text", raise_read_error)

    with pytest.raises(HTTPException) as error:
        resume_pipeline.analyze_uploaded_resume(
            filename="broken.pdf",
            file_bytes=b"not a valid PDF",
        )

    assert error.value.status_code == 422