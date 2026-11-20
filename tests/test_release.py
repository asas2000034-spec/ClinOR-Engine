from pathlib import Path

from fastapi.testclient import TestClient

from clinor.api import app
from clinor.optimizer import optimize
from clinor.reviews import model_digest
from clinor.schemas import OptimizeRequest


def test_cloud_probe_requires_consent(monkeypatch):
    monkeypatch.setenv("CLINOR_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("CLINOR_LLM_DEPLOYMENT", "cloud")
    monkeypatch.setenv("CLINOR_ALLOW_CLOUD_LLM", "1")
    monkeypatch.setenv("CLINOR_LLM_MODEL", "test")
    monkeypatch.setenv("CLINOR_LLM_API_KEY", "synthetic")
    assert TestClient(app).post("/api/llm/check").status_code == 403


def test_exact_model_approval(monkeypatch, tmp_path):
    monkeypatch.setenv("CLINOR_REVIEW_DIRECTORY", str(tmp_path))
    request = OptimizeRequest(
        mode="clinical",
        options=[{"option_id": "A", "label": "A", "benefit": 1, "burden": 0, "cost": 1}],
        guideline_approval={
            "scope": "synthetic",
            "guideline_url": "https://example.org",
            "guideline_version": "1",
            "approved_by": "Synthetic reviewer",
            "approved_on": "2026-01-01",
        },
    )
    assert optimize(request).status == "review_required"
    (tmp_path / (model_digest(request) + ".json")).write_text(
        '{"revision":1,"state":"approved","change_note":"Synthetic test","effective_from":"2020-01-01T00:00:00Z","expires_at":"2100-01-01T00:00:00Z"}'
    )
    assert optimize(request).status == "optimal"
    request.options[0].cost = 2
    assert optimize(request).status == "review_required"


def test_static_language_and_assets():
    client = TestClient(app)
    for path in Path("clinor/static").glob("*"):
        if path.suffix in {".html", ".js"}:
            assert not any("\u0600" <= char <= "\u06ff" for char in path.read_text(encoding="utf8"))
    assert client.get("/static/brand/wordmark-reversed.svg").status_code == 200
