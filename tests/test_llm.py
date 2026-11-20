"""Transport-level integration tests, no model download or real network required."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from clinor.ai import explain_methods, plan_queries, synthesize
from clinor.api import app
from clinor.evidence import article_to_evidence
from clinor.llm import LLMGateway, LLMSettings, LLMUnavailable, parse_json_object
from clinor.research import research
from clinor.schemas import ResearchRequest


def mock_gateway(provider="ollama", response=None, *, deployment="local"):
    result = response or {"ok": True}
    def responder(req):
        if provider == "ollama":
            assert str(req.url).endswith("/api/chat")
            assert req.method == "POST"
            body = json.loads(req.content)
            assert body["stream"] is False
            assert body["format"] == "json"
            return httpx.Response(200, json={"message": {"content": json.dumps(result)}})
        assert str(req.url).endswith("/v1/chat/completions")
        body = json.loads(req.content)
        assert body["response_format"] == {"type": "json_object"}
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(result)}}]})
    settings = LLMSettings(provider=provider, model="test-model", deployment=deployment,
                           base_url=("http://localhost:11434" if provider == "ollama"
                                     else "http://127.0.0.1:1234/v1"))
    return LLMGateway(settings, httpx.AsyncClient(transport=httpx.MockTransport(responder)))


@pytest.mark.asyncio
async def test_ollama_native_transport():
    llm = mock_gateway()
    assert (await llm.check())["connected"] is True
    await llm.client.aclose()


@pytest.mark.asyncio
async def test_openai_compatible_local_transport():
    llm = mock_gateway("openai_compatible")
    assert (await llm.check())["provider"] == "openai_compatible"
    await llm.client.aclose()


def test_json_validation():
    assert parse_json_object('```json\n{"ok":true}\n```') == {"ok": True}
    with pytest.raises(LLMUnavailable):
        parse_json_object('["array"]')
    with pytest.raises(LLMUnavailable):
        parse_json_object('Here is the answer')


def test_llm_endpoint_remote_host_blocked(monkeypatch):
    monkeypatch.delenv("CLINOR_LLM_TRUSTED_HOSTS", raising=False)
    with pytest.raises(LLMUnavailable, match="not trusted"):
        LLMSettings("openai_compatible", "test", "http://evil.invalid/v1", "local").validate()


def test_cloud_requires_explicit_server_opt_in(monkeypatch):
    monkeypatch.delenv("CLINOR_ALLOW_CLOUD_LLM", raising=False)
    with pytest.raises(LLMUnavailable, match="CLINOR_ALLOW_CLOUD_LLM"):
        LLMSettings("openai_compatible", "test", "https://api.openai.com/v1", "cloud", "secret").validate()


@pytest.mark.asyncio
async def test_query_plan_generic_specialty():
    llm = mock_gateway(response={"queries": ["asthma guideline", "asthma systematic review", "asthma trial"]})
    assert len(await plan_queries("asthma", "What treatments?", llm)) == 3
    await llm.client.aclose()


@pytest.mark.asyncio
async def test_evidence_id_filtering_prevents_fabricated_references():
    evidence = [article_to_evidence({"title": "Randomized trial", "pubYear": "2025", "pmid": "12345"})]
    llm = mock_gateway(response={"findings": [
        {"statement": "Unsupported", "evidence_ids": ["pmid:fake"], "confidence": "high"},
        {"statement": "Preliminary", "evidence_ids": ["pmid:12345"], "confidence": "moderate"}],
        "gaps": ["Requires full-text verification"]})
    findings, gaps = await synthesize("Any results?", evidence, llm)
    assert len(findings) == 1
    assert findings[0].evidence_ids == ["pmid:12345"]
    assert gaps
    await llm.client.aclose()


@pytest.mark.asyncio
async def test_research_uses_local_llm_and_discovery_pipeline():
    requests = []
    def responder(req):
        inputs = json.loads(req.content)
        requests.append(inputs)
        if "Create exactly 3" in inputs["messages"][0]["content"]:
            data = {"queries": ["heart failure guideline"]}
        else:
            data = {"findings": [{"statement": "Review candidate", "evidence_ids": ["pmid:12345"],
                                  "confidence": "low"}], "gaps": ["Verify full text"]}
        return httpx.Response(200, json={"message": {"content": json.dumps(data)}})
    llm = LLMGateway(LLMSettings("ollama", "test", "http://localhost:11434", "local"),
                     httpx.AsyncClient(transport=httpx.MockTransport(responder)))
    class FakeEuropePMC:
        async def search(self, query, limit=12):
            return [article_to_evidence({"title": "A guideline candidate", "pubYear": "2026",
                                         "pmid": "12345"})]
    response = await research(ResearchRequest(condition="heart failure", use_ai=True,
                                              consent_external_search=True),
                              provider=FakeEuropePMC(), llm_gateway=llm)
    assert response.ai_enabled is True
    assert response.llm_provider == "ollama"
    assert len(requests) == 2
    assert response.findings[0].evidence_ids == ["pmid:12345"]
    await llm.client.aclose()


@pytest.mark.asyncio
async def test_no_cloud_consent_means_no_model_call(monkeypatch):
    monkeypatch.setenv("CLINOR_ALLOW_CLOUD_LLM", "1")
    class CrashingClient:
        async def post(self, *a, **kw):
            raise AssertionError("Cloud LLM must not be contacted")
    cloud = LLMGateway(LLMSettings("openai_compatible", "test", "https://api.openai.com/v1", "cloud", "key"),
                       CrashingClient())
    class FakeProvider:
        async def search(self, query, limit=12):
            return []
    response = await research(ResearchRequest(condition="heart failure", use_ai=True,
                                              consent_external_search=True, consent_cloud_llm=False),
                              provider=FakeProvider(), llm_gateway=cloud)
    assert response.ai_enabled is False
    assert any("Cloud LLM not used" in n for n in response.notices)


@pytest.mark.asyncio
async def test_no_literature_consent_blocks_all_requests():
    class CrashingModel:
        @property
        def settings(self):
            raise AssertionError("LLM settings should not be read")
    resp = await research(ResearchRequest(condition="rheumatoid arthritis"),
                          llm_gateway=CrashingModel())
    assert resp.status == "consent_required"


@pytest.mark.asyncio
async def test_llm_explains_only_given_method_candidates():
    llm = mock_gateway(response={"explanation": "MCDA compares multiple criteria.",
                                 "data_needed": ["Criterion weights"]})
    output = await explain_methods("Compare choices", [{"algorithm": "mcda", "reason": "Multiple objectives"}], llm)
    assert output["data_needed"] == ["Criterion weights"]
    await llm.client.aclose()


def test_status_endpoint_never_discloses_keys(monkeypatch):
    monkeypatch.setenv("CLINOR_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("CLINOR_LLM_MODEL", "local-model")
    monkeypatch.setenv("CLINOR_LLM_API_KEY", "private-token")
    response = TestClient(app).get("/api/llm/status")
    assert response.status_code == 200
    assert response.json()["model"] == "local-model"
    assert "private-token" not in response.text


def test_method_endpoint_cloud_consent_required(monkeypatch):
    monkeypatch.setenv("CLINOR_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("CLINOR_LLM_DEPLOYMENT", "cloud")
    monkeypatch.setenv("CLINOR_ALLOW_CLOUD_LLM", "1")
    monkeypatch.setenv("CLINOR_LLM_API_KEY", "test-secret")
    monkeypatch.setenv("CLINOR_LLM_MODEL", "mock-model")
    result = TestClient(app).post("/api/llm/method-advice", json={
        "problem": {"problem_type": "Compare criteria", "has_multiple_criteria": True}})
    assert result.status_code == 403


def test_route_without_server_does_not_auto_run_solver(monkeypatch):
    monkeypatch.setenv("CLINOR_LLM_PROVIDER", "disabled")
    result = TestClient(app).post("/api/llm/method-advice", json={
        "problem": {"problem_type": "Compare criteria", "has_multiple_criteria": True}})
    assert result.status_code == 503
    assert TestClient(app).post("/api/or/recommend", json={
        "problem_type": "Compare criteria", "has_multiple_criteria": True}).status_code == 200
