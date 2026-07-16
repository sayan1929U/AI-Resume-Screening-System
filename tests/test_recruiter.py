import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.api import recruiter
from app.db.models import Analysis, Resume
from app.db.session import AsyncSessionLocal
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client


async def signup_and_get_token(client, email, role):
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": "SecurePassword123!",
            "role": role,
        },
    )

    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_recruiter_dashboard_is_available(client):
    response = await client.get("/api/recruiter")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_recruiter_history_requires_login(client):
    response = await client.get("/api/recruiter/history")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_candidate_cannot_view_recruiter_history(client):
    token = await signup_and_get_token(
        client,
        email="candidate@example.com",
        role="candidate",
    )

    response = await client.get(
        "/api/recruiter/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_recruiter_can_view_saved_history(client):
    token = await signup_and_get_token(
        client,
        email="recruiter@example.com",
        role="recruiter",
    )

    async with AsyncSessionLocal() as session:
        resume = Resume(filename="candidate_resume.pdf")
        session.add(resume)
        await session.flush()

        analysis = Analysis(
            resume_id=resume.id,
            ats_score=85,
            job_match=80,
            semantic_match=75,
            project_score=70,
            overall_score=77.5,
            rank=1,
            recommendation="Strong candidate",
            matching_skills=["Python", "FastAPI"],
            missing_skills=["Docker"],
        )
        session.add(analysis)
        await session.commit()

    response = await client.get(
        "/api/recruiter/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["history"][0]["filename"] == "candidate_resume.pdf"
    assert data["history"][0]["ats_score"] == 85
    assert data["history"][0]["matching_skills"] == ["Python", "FastAPI"]


@pytest.mark.asyncio
async def test_recruiter_upload_rejects_more_than_100_files(client):
    token = await signup_and_get_token(
        client,
        email="limit_recruiter@example.com",
        role="recruiter",
    )

    files = [
        ("files", ("resume.pdf", b"1", "application/pdf"))
        for _ in range(101)
    ]

    response = await client.post(
        "/api/recruiter/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Maximum 100 resumes allowed."


@pytest.mark.asyncio
async def test_recruiter_upload_ranks_and_saves_successful_resumes(client, monkeypatch):
    token = await signup_and_get_token(
        client,
        email="upload_recruiter@example.com",
        role="recruiter",
    )

    def fake_analyze_uploaded_resume(filename, file_bytes):
        results = {
            "alice.pdf": {
                "filename": "alice.pdf",
                "ats_score": 80,
                "job_match": 70,
                "semantic_match": 60,
                "project_score": 50,
                "recommendation": "Strong candidate",
                "matching_skills": ["Python", "FastAPI"],
                "missing_skills": ["Docker"],
            },
            "bob.pdf": {
                "filename": "bob.pdf",
                "ats_score": 90,
                "job_match": 50,
                "semantic_match": 40,
                "project_score": 20,
                "recommendation": "Potential candidate",
                "matching_skills": ["Python"],
                "missing_skills": ["FastAPI"],
            },
        }
        return results[filename]

    monkeypatch.setattr(
        recruiter,
        "analyze_uploaded_resume",
        fake_analyze_uploaded_resume,
    )

    response = await client.post(
        "/api/recruiter/upload",
        files=[
            ("files", ("alice.pdf", b"alice resume", "application/pdf")),
            ("files", ("bob.pdf", b"bob resume", "application/pdf")),
        ],
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_candidates"] == 2
    assert data["failed"] == 0
    assert data["candidates"][0]["filename"] == "alice.pdf"
    assert data["candidates"][0]["rank"] == 1
    assert data["candidates"][0]["overall_score"] == 67.5

    async with AsyncSessionLocal() as session:
        resumes = (await session.execute(select(Resume))).scalars().all()
        analyses = (await session.execute(select(Analysis))).scalars().all()

    assert len(resumes) == 2
    assert len(analyses) == 2


@pytest.mark.asyncio
async def test_recruiter_upload_reports_failed_resume(client, monkeypatch):
    token = await signup_and_get_token(
        client,
        email="error_recruiter@example.com",
        role="recruiter",
    )

    def fake_analyze_uploaded_resume(filename, file_bytes):
        if filename == "broken.pdf":
            raise HTTPException(status_code=400, detail="Unreadable resume.")

        return {
            "filename": filename,
            "ats_score": 80,
            "job_match": 70,
            "semantic_match": 60,
            "project_score": 50,
            "recommendation": "Strong candidate",
            "matching_skills": ["Python"],
            "missing_skills": [],
        }

    monkeypatch.setattr(
        recruiter,
        "analyze_uploaded_resume",
        fake_analyze_uploaded_resume,
    )

    response = await client.post(
        "/api/recruiter/upload",
        files=[
            ("files", ("valid.pdf", b"valid resume", "application/pdf")),
            ("files", ("broken.pdf", b"broken resume", "application/pdf")),
        ],
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total_candidates"] == 1
    assert data["failed"] == 1
    assert data["errors"] == [
        {
            "filename": "broken.pdf",
            "error": "Unreadable resume.",
        }
    ]