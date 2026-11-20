from fastapi.testclient import TestClient

from clinor.api import app


def test_health_and_frontpage():
    client = TestClient(app)
    assert client.get("/api/health").json()["ok"] is True
    assert "EVIDORIX" in client.get("/").text


def test_request_validation():
    response = TestClient(app).post("/api/research", json={"condition": "x"})
    assert response.status_code == 422
