import pytest
from httpx import ASGITransport, AsyncClient

from app.api import upload
from app.main import app


@pytest.mark.asyncio
async def test_upload_sends_file_data_to_pipeline(monkeypatch):
    captured = {}

    def fake_analyze_uploaded_resume(**kwargs):
        captured.update(kwargs)
        return {
            "message": "Resume analyzed successfully.",
            "filename": kwargs["filename"],
            "ats_score": 90,
        }

    monkeypatch.setattr(
        upload,
        "analyze_uploaded_resume",
        fake_analyze_uploaded_resume,
    )

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/upload/upload",
            files={
                "file": (
                    "resume.pdf",
                    b"fake resume contents",
                    "application/pdf",
                )
            },
            data={
                "candidate_name": "Asha",
                "role": "Backend Developer",
                "job_description": "Python and FastAPI",
            },
        )

    assert response.status_code == 200
    assert response.json()["ats_score"] == 90
    assert captured["filename"] == "resume.pdf"
    assert captured["candidate_name"] == "Asha"
    assert captured["role"] == "Backend Developer"


@pytest.mark.asyncio
async def test_upload_rejects_file_larger_than_limit(monkeypatch):
    # Small limit makes the test fast and avoids creating a 10 MB test file.
    monkeypatch.setattr(upload, "MAX_FILE_SIZE_BYTES", 5)

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/upload/upload",
            files={
                "file": (
                    "large.pdf",
                    b"123456",
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 413
    assert response.json()["detail"] == "File is larger than the 10MB limit."