from __future__ import annotations

from collections import deque
from pathlib import Path
from time import monotonic
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__
from .ai import explain_methods
from .llm import LLMGateway, LLMUnavailable, llm_status
from .optimizer import optimize
from .or_engine import (
    cp_sat,
    dynamic_programming,
    markov,
    mcda,
    monte_carlo,
    pareto,
    queueing,
    scenario_optimization,
)
from .or_engine.models import (
    CPSATRequest,
    DynamicRequest,
    MarkovRequest,
    MCDARequest,
    MonteCarloRequest,
    ORResult,
    ParetoRequest,
    QueueingRequest,
    ScenarioRequest,
)
from .or_engine.router import RoutingRequest, recommend_techniques
from .research import research
from .schemas import OptimizeRequest, OptimizeResponse, ResearchRequest, ResearchResponse

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="EVIDORIX Engine", version=__version__, description=(
    "Research-oriented clinical evidence discovery and supervised decision optimization. "
    "Not autonomous clinical decision making."))
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


# A single process-wide budget bounds work without retaining client identifiers.
_recent_requests: deque[float] = deque()


@app.middleware("http")
async def request_budget(request: Request, call_next):
    audit_id = uuid4().hex
    if request.method == "POST":
        now = monotonic()
        while _recent_requests and _recent_requests[0] <= now - 60:
            _recent_requests.popleft()
        if len(_recent_requests) >= 120:
            return JSONResponse({"detail": "Request budget reached"}, status_code=429,
                                headers={"Retry-After": "60", "X-Request-ID": audit_id})
        _recent_requests.append(now)
    response = await call_next(request)
    response.headers["X-Request-ID"] = audit_id
    return response


@app.get("/")
def homepage():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"ok": True, "name": "EVIDORIX Engine", "version": __version__}


@app.get("/api/llm/status")
def model_status():
    """Describe the configured model without exposing API keys or invoking the provider."""
    return llm_status()


@app.post("/api/llm/check")
async def model_connection_check(consent_cloud_llm: bool = False):
    try:
        gateway = LLMGateway()
        if gateway.settings.deployment == "cloud" and not consent_cloud_llm:
            raise HTTPException(status_code=403, detail="Explicit cloud test consent is required")
        return await gateway.check()
    except LLMUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


class MethodAdviceRequest(BaseModel):
    problem: RoutingRequest
    consent_cloud_llm: bool = False


@app.post("/api/llm/method-advice")
async def method_advice(req: MethodAdviceRequest):
    """Only explains deterministic solver candidates; does not run clinical decision algorithms."""
    routing = recommend_techniques(req.problem)
    try:
        gateway = LLMGateway()
        if gateway.settings.deployment == "cloud" and not req.consent_cloud_llm:
            raise HTTPException(status_code=403, detail="Explicit cloud LLM consent is required")
        commentary = await explain_methods(req.problem.problem_type, routing["suggestions"], gateway)
        return {"routing": routing, "ai": commentary, "provider": gateway.settings.provider,
                "model": gateway.settings.model, "notice": "Method advice is unvalidated and does not execute any solver."}
    except LLMUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/research", response_model=ResearchResponse)
async def research_endpoint(request: ResearchRequest):
    return await research(request)


@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize_endpoint(request: OptimizeRequest):
    return optimize(request)


@app.get("/api/or/algorithms")
def or_algorithms():
    """Machine-readable inventory: availability != clinical validation."""
    import importlib.util
    return {"engines": [
        {"id": "milp", "endpoint": "/api/optimize", "available": True},
        {"id": "mcda", "endpoint": "/api/or/mcda", "available": True},
        {"id": "pareto", "endpoint": "/api/or/pareto", "available": True},
        {"id": "scenarios", "endpoint": "/api/or/scenarios", "available": True,
         "strategies": ["expected_value", "maximin"]},
        {"id": "monte_carlo", "endpoint": "/api/or/monte-carlo", "available": True},
        {"id": "markov", "endpoint": "/api/or/markov", "available": True},
        {"id": "dynamic_programming", "endpoint": "/api/or/dynamic-programming", "available": True},
        {"id": "queueing", "endpoint": "/api/or/queueing", "available": True},
        {"id": "cp_sat", "endpoint": "/api/or/cp-sat",
         "available": importlib.util.find_spec("ortools") is not None},
    ], "research_scope": "condition-agnostic",
       "clinical_validation": "not established"}


@app.post("/api/or/recommend")
def technique_recommendation(req: RoutingRequest):
    return recommend_techniques(req)


@app.post("/api/or/mcda", response_model=ORResult)
def mcda_endpoint(req: MCDARequest):
    return mcda(req)


@app.post("/api/or/pareto", response_model=ORResult)
def pareto_endpoint(req: ParetoRequest):
    return pareto(req)


@app.post("/api/or/scenarios", response_model=ORResult)
def scenarios_endpoint(req: ScenarioRequest):
    return scenario_optimization(req)


@app.post("/api/or/monte-carlo", response_model=ORResult)
def monte_carlo_endpoint(req: MonteCarloRequest):
    return monte_carlo(req)


@app.post("/api/or/markov", response_model=ORResult)
def markov_endpoint(req: MarkovRequest):
    return markov(req)


@app.post("/api/or/dynamic-programming", response_model=ORResult)
def dynamic_endpoint(req: DynamicRequest):
    return dynamic_programming(req)


@app.post("/api/or/queueing", response_model=ORResult)
def queue_endpoint(req: QueueingRequest):
    return queueing(req)


@app.post("/api/or/cp-sat", response_model=ORResult)
def cp_endpoint(req: CPSATRequest):
    return cp_sat(req)
