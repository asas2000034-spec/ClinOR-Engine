"""Regression tests for opt-in API authentication and response security."""
from __future__ import annotations

from fastapi.testclient import TestClient

from clinor.api import app


KEY = "test-only-random-secret-with-minimum-length-12345"


def test_local_development_stays_compatible(monkeypatch):
    monkeypatch.delenv("CLINOR_AUTH_REQUIRED", raising=False)
    monkeypatch.delenv("CLINOR_API_KEY", raising=False)
    client = TestClient(app)
    response = client.get("/api/or/algorithms")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Cache-Control"] == "no-store"


def test_enabled_without_key_fails_closed(monkeypatch):
    monkeypatch.setenv("CLINOR_AUTH_REQUIRED", "true")
    monkeypatch.delenv("CLINOR_API_KEY", raising=False)
    client = TestClient(app)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/or/algorithms").status_code == 503


def test_api_requires_valid_secret(monkeypatch):
    monkeypatch.setenv("CLINOR_AUTH_REQUIRED", "true")
    monkeypatch.setenv("CLINOR_API_KEY", KEY)
    client = TestClient(app)
    assert client.get("/api/or/algorithms").status_code == 401
    assert client.get("/api/or/algorithms", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/api/or/algorithms", headers={"X-API-Key": KEY}).status_code == 200
    assert client.get("/api/or/algorithms", headers={"Authorization": "Bearer " + KEY}).status_code == 200


def test_key_without_required_flag_still_enforces_auth(monkeypatch):
    monkeypatch.delenv("CLINOR_AUTH_REQUIRED", raising=False)
    monkeypatch.setenv("CLINOR_API_KEY", KEY)
    client = TestClient(app)
    assert client.get("/api/or/algorithms").status_code == 401


def test_frontpage_is_public_but_api_stays_protected(monkeypatch):
    monkeypatch.setenv("CLINOR_AUTH_REQUIRED", "1")
    monkeypatch.setenv("CLINOR_API_KEY", KEY)
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/api/or/algorithms").status_code == 401
    assert "X-Request-ID" in client.get("/api/or/algorithms").headers
