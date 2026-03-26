"""
Backend API tests for Interview Tester.
Run with: python -m pytest tests/ -v
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    """Use a temporary database for each test."""
    import app.database as db_module
    db_module.DATABASE_PATH = str(tmp_path / "test.db")
    import asyncio
    asyncio.run(init_db())
    yield


class TestHealth:
    def test_health_endpoint(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "llm_status" in data
        assert "llm_provider" in data
        assert "model" in data


class TestUsers:
    def test_create_user(self):
        response = client.post("/api/users", json={"name": "Test Student"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Student"
        assert "id" in data
        assert "created_at" in data

    def test_list_users(self):
        client.post("/api/users", json={"name": "Alice"})
        client.post("/api/users", json={"name": "Bob"})
        response = client.get("/api/users")
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 2

    def test_get_user(self):
        create = client.post("/api/users", json={"name": "Charlie"})
        user_id = create.json()["id"]
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Charlie"

    def test_get_nonexistent_user(self):
        response = client.get("/api/users/9999")
        assert response.status_code == 404


class TestProfile:
    @patch("app.services.profile_extractor.ollama.generate", new_callable=AsyncMock)
    def test_extract_profile(self, mock_generate):
        mock_generate.return_value = '{"education": {"level": "secondary", "institution": "Test School"}, "skills": ["Python", "React"], "experience": null, "projects": [{"name": "Interview Tester", "description": "AI app", "technologies": ["Python", "React"], "role": "developer", "outcome": "completed"}], "goals": "study CS at CUHK", "target_programs": ["Computer Science"], "target_universities": ["CUHK"], "achievements": ["Dean\'s List"], "interests": ["AI"], "personality_traits": ["curious"]}'

        # Create user first
        user = client.post("/api/users", json={"name": "Test"}).json()

        response = client.post("/api/profile/extract", json={
            "user_id": user["id"],
            "transcript": "I am a student who built an Interview Tester app."
        })
        assert response.status_code == 200
        profile = response.json()
        assert profile["skills"] is not None
        assert profile["user_id"] == user["id"]

    def test_extract_profile_no_user(self):
        response = client.post("/api/profile/extract", json={
            "user_id": 9999,
            "transcript": "hello"
        })
        assert response.status_code == 404


class TestInterview:
    @patch("app.services.conversation_engine.ollama.generate", new_callable=AsyncMock)
    @patch("app.services.profile_extractor.ollama.generate", new_callable=AsyncMock)
    def test_start_interview(self, mock_extract, mock_question):
        mock_extract.return_value = '{"education": null, "skills": ["Python"], "experience": null, "projects": null, "goals": "study CS", "target_programs": null, "target_universities": ["CUHK"], "achievements": null, "interests": null, "personality_traits": null}'
        mock_question.return_value = "Tell me about yourself and why you want to study at CUHK."

        user = client.post("/api/users", json={"name": "Test"}).json()
        client.post("/api/profile/extract", json={
            "user_id": user["id"],
            "transcript": "I like coding."
        })

        response = client.post("/api/interview/start", json={
            "user_id": user["id"],
            "target_university": "CUHK",
            "target_program": "Engineering",
            "mode": "practice",
            "difficulty": "medium",
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "question_text" in data
        assert data["question_number"] == 1

    def test_start_interview_no_profile(self):
        user = client.post("/api/users", json={"name": "NoProfile"}).json()
        response = client.post("/api/interview/start", json={
            "user_id": user["id"],
            "target_university": "CUHK",
        })
        assert response.status_code == 400


class TestBriefing:
    def test_get_programs(self):
        response = client.get("/api/briefing/programs")
        assert response.status_code == 200
        programs = response.json()["programs"]
        assert "Medicine" in programs
        assert "Engineering" in programs
        assert len(programs) >= 9

    def test_get_interview_format(self):
        response = client.get("/api/briefing/format?university=CUHK&program=Medicine")
        assert response.status_code == 200
        data = response.json()
        assert "MMI" in data["format"]
        assert len(data["competencies"]) > 0
