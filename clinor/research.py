"""Cross-specialty evidence discovery; local-first LLM, explicit third-party consent."""
from __future__ import annotations

import os

import httpx

from .ai import fallback_queries, plan_queries, synthesize
from .evidence import EuropePMC, rank_evidence
from .llm import LLMGateway, LLMUnavailable
from .openai_web import OpenAIWebGuidelineSearch
from .schemas import ResearchRequest, ResearchResponse
from .web_guidelines import BraveGuidelineSearch


async def research(req: ResearchRequest, provider: EuropePMC | None = None,
                   web_provider: BraveGuidelineSearch | None = None,
                   ai_web_provider: OpenAIWebGuidelineSearch | None = None,
                   llm_gateway: LLMGateway | None = None) -> ResearchResponse:
    if not req.consent_external_search:
        return ResearchResponse(
            status="consent_required", condition=req.condition,
            notices=["External literature discovery requires consent. Use de-identified topic terms only."],
        )
    notices = ["Found publications are discovery candidates, not validated guideline rules.",
               "LLM summaries are preliminary; abstracts cannot establish individual treatment suitability."]
    gateway = None
    if req.use_ai:
        try:
            gateway = llm_gateway or LLMGateway()
            if gateway.settings.provider == "disabled":
                notices.append("LLM disabled by CLINOR_LLM_PROVIDER.")
                gateway = None
            elif gateway.settings.deployment == "cloud" and not req.consent_cloud_llm:
                notices.append("Cloud LLM not used: explicit consent_cloud_llm=true required.")
                gateway = None
        except (LLMUnavailable, ValueError) as exc:
            notices.append(f"LLM configuration unavailable: {exc}")
    queries = fallback_queries(req.condition)
    if gateway:
        try:
            queries = await plan_queries(req.condition, req.question, gateway)
        except LLMUnavailable as exc:
            notices.append(f"LLM query planning unavailable; deterministic queries used: {exc}")
        except (ValueError, TypeError, KeyError):
            notices.append("LLM query planning failed; deterministic queries used.")
    provider = provider or EuropePMC()
    all_records = []
    successes = 0
    for query in queries:
        try:
            all_records.extend(await provider.search(query, limit=req.max_results))
            successes += 1
        except (httpx.HTTPError, ValueError) as exc:
            notices.append(f"A literature source request failed: {type(exc).__name__}")
    if os.getenv("BRAVE_SEARCH_API_KEY"):
        try:
            guideline_web = await (web_provider or BraveGuidelineSearch()).search(
                req.condition, req.jurisdiction, limit=min(req.max_results, 10))
            all_records.extend(guideline_web)
            successes += 1
        except (httpx.HTTPError, ValueError) as exc:
            notices.append(f"Guideline web search failed: {type(exc).__name__}")
    else:
        notices.append("Publisher website search optional: set BRAVE_SEARCH_API_KEY.")
    if req.use_ai and req.consent_cloud_llm and os.getenv("OPENAI_WEB_SEARCH") == "1":
        try:
            all_records.extend((ai_web_provider or OpenAIWebGuidelineSearch()).search(
                req.condition, req.jurisdiction))
            successes += 1
        except Exception:  # noqa: BLE001 - isolate optional third-party SDK failures
            notices.append("Optional cloud AI web discovery failed; indexed evidence remains available.")
    elif os.getenv("OPENAI_WEB_SEARCH") == "1":
        notices.append("OpenAI web discovery not used: consent_cloud_llm=true required.")
    ranked = rank_evidence(all_records, req.max_results)
    if not successes:
        return ResearchResponse(status="source_unavailable", condition=req.condition,
                                search_queries=queries, notices=notices)
    findings = []
    gaps = []
    ai_enabled = False
    if gateway and ranked:
        try:
            findings, gaps = await synthesize(req.question, ranked, gateway)
            ai_enabled = True
        except LLMUnavailable as exc:
            notices.append(f"LLM evidence brief unavailable: {exc}")
        except (ValueError, TypeError, KeyError):
            notices.append("LLM evidence brief failed. Source metadata remains available.")
    if not ranked:
        gaps.append("No indexed records found. This does not prove that no guideline exists.")
    elif gateway is None:
        notices.append("AI synthesis inactive; configure a local or permitted cloud LLM.")
    return ResearchResponse(status="completed", condition=req.condition,
                            search_queries=queries, evidence=ranked, ai_enabled=ai_enabled,
                            llm_provider=gateway.settings.provider if ai_enabled else None,
                            llm_model=gateway.settings.model if ai_enabled else None,
                            findings=findings, unresolved_questions=gaps, notices=notices)
