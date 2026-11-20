from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ResearchRequest(BaseModel):
    condition: str = Field(min_length=3, max_length=180)
    question: str = Field(default="Which guidelines and high-quality evidence are relevant?", max_length=500)
    jurisdiction: str = Field(default="international", max_length=60)
    max_results: int = Field(default=12, ge=1, le=30)
    consent_external_search: bool = False
    use_ai: bool = True
    consent_cloud_llm: bool = False


class Evidence(BaseModel):
    evidence_id: str
    title: str
    url: str
    source: str
    year: int | None = None
    doi: str | None = None
    pmid: str | None = None
    publication_date: str | None = None
    jurisdiction: str | None = None
    guideline_version: str | None = None
    last_reviewed: str | None = None
    journal: str | None = None
    abstract: str | None = None
    publication_types: list[str] = Field(default_factory=list)
    evidence_category: str = "unclassified"
    status: Literal["discovered_unverified", "reviewed"] = "discovered_unverified"
    collected_at: str = Field(default_factory=utc_now)


class Finding(BaseModel):
    statement: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: Literal["low", "moderate", "high"] = "low"


class ResearchResponse(BaseModel):
    status: Literal["consent_required", "completed", "source_unavailable"]
    condition: str
    search_queries: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    ai_enabled: bool = False
    llm_provider: str | None = None
    llm_model: str | None = None
    findings: list[Finding] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    notices: list[str] = Field(default_factory=list)


class TreatmentOption(BaseModel):
    option_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    label: str = Field(min_length=1, max_length=180)
    benefit: float = Field(ge=0, le=100, description="Reviewer-entered normalized score")
    burden: float = Field(ge=0, le=100)
    cost: float = Field(ge=0)
    forbidden: bool = False
    evidence_ids: list[str] = Field(default_factory=list)
    incompatible_with: list[str] = Field(default_factory=list)
    requires: list[str] = Field(default_factory=list)


class GuidelineApproval(BaseModel):
    scope: str = Field(min_length=3)
    guideline_url: HttpUrl
    guideline_version: str = Field(min_length=1)
    approved_by: str = Field(min_length=3)
    approved_on: str = Field(min_length=8)


class OptimizeRequest(BaseModel):
    mode: Literal["sandbox", "clinical"] = "sandbox"
    options: list[TreatmentOption] = Field(min_length=1, max_length=60)
    max_selections: int = Field(default=1, ge=1, le=60)
    min_selections: int = Field(default=1, ge=0, le=60)
    budget: float | None = Field(default=None, ge=0)
    benefit_weight: float = Field(default=1.0, ge=0, le=100)
    burden_weight: float = Field(default=1.0, ge=0, le=100)
    cost_weight: float = Field(default=0.0, ge=0, le=100)
    guideline_approval: GuidelineApproval | None = None

    @model_validator(mode="after")
    def check_consistency(self):
        names = [o.option_id for o in self.options]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate option_id")
        if self.min_selections > self.max_selections:
            raise ValueError("min_selections cannot exceed max_selections")
        for option in self.options:
            if not set(option.requires + option.incompatible_with).issubset(set(names)):
                raise ValueError(f"Unknown option referenced by {option.option_id}")
            if option.option_id in option.incompatible_with or option.option_id in option.requires:
                raise ValueError("Options cannot refer to themselves")
        return self


class OptimizeResponse(BaseModel):
    status: Literal["optimal", "feasible", "infeasible", "review_required", "solver_error"]
    selected: list[str] = Field(default_factory=list)
    objective: float | None = None
    explanation: str
    clinical_authorization: Literal["not_authorized", "requires_clinician_confirmation"] = "not_authorized"
    caveats: list[str] = Field(default_factory=list)
