import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_signup_returns_access_token(client):
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": "recruiter@example.com",
            "password": "SecurePassword123!",
            "role": "recruiter",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_duplicate_signup_is_rejected(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
        "role": "recruiter",
    }

    first_response = await client.post("/api/auth/signup", json=payload)
    second_response = await client.post("/api/auth/signup", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email is already registered."


@pytest.mark.asyncio
async def test_login_returns_access_token(client):
    email = "login@example.com"
    password = "SecurePassword123!"

    signup_response = await client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": password,
            "role": "candidate",
        },
    )
    assert signup_response.status_code == 201

    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(client):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."