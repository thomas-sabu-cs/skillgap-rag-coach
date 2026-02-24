"""Tests for /analyze endpoint and match score calculation."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app, get_session


async def mock_get_session():
    """Yield a mock session so tests don't require Postgres."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock(return_value=None)
    session.rollback = AsyncMock(return_value=None)
    try:
        yield session
    finally:
        pass


async def noop_init_db() -> None:
    pass


@pytest.fixture
def client() -> TestClient:
    # Avoid hitting real DB during startup and request
    app.dependency_overrides[get_session] = mock_get_session
    with patch("main.init_db", noop_init_db):
        with TestClient(app) as c:
            yield c
    app.dependency_overrides.pop(get_session, None)


def test_analyze_match_score_calculation(client: TestClient) -> None:
    """Submit resume and job description; assert match score is computed correctly."""
    resume = "Backend engineer. Python, PostgreSQL, Docker, REST APIs. Used FastAPI and git."
    job = "We need Python, PostgreSQL, Docker, and Kubernetes. REST experience required."
    response = client.post(
        "/analyze",
        json={"resume_text": resume, "job_description": job},
    )
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data
    assert isinstance(data["match_score"], int)
    assert 0 <= data["match_score"] <= 100
    # Job skills: python, postgresql, docker, kubernetes, rest (5). Resume has python, postgresql, docker, rest (4). 4/5 = 80%
    assert data["match_score"] == 80
    assert "overlapping_skills" in data
    assert isinstance(data["overlapping_skills"], list)
    for item in data["overlapping_skills"]:
        assert "skill" in item
        assert "evidence" in item
    assert "missing_skills" in data
    assert "kubernetes" in data["missing_skills"] or "k8s" in data["missing_skills"]
    assert data["mode"] in ("baseline", "llm")
