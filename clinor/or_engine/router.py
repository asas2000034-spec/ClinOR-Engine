"""Auditable, non-LLM technique suggestions; never substitutes for model validation."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RoutingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    problem_type: str = Field(min_length=4, max_length=350)
    has_probabilities: bool = False
    decisions_are_sequential: bool = False
    has_multiple_criteria: bool = False
    has_resource_constraints: bool = False
    need_uncertainty_analysis: bool = False
    is_patient_flow: bool = False


def recommend_techniques(req: RoutingRequest) -> dict:
    match = []
    if req.is_patient_flow:
        match.append({"algorithm": "queueing", "reason": "Service capacity and waiting times."})
    if req.decisions_are_sequential:
        match.append({"algorithm": "dynamic_programming", "reason": "Sequential state-dependent actions."})
        if req.has_probabilities:
            match.append({"algorithm": "markov", "reason": "Probabilistic state-transition outcomes."})
    if req.has_resource_constraints:
        match.extend([{"algorithm": "milp", "reason": "Hard combinatorial/resource constraints."},
                      {"algorithm": "cp_sat", "reason": "Discrete logical constraints."}])
    if req.has_multiple_criteria:
        match.extend([{"algorithm": "pareto", "reason": "Identify nondominated alternatives."},
                      {"algorithm": "mcda", "reason": "Transparent weighted preference analysis."}])
    if req.need_uncertainty_analysis:
        match.append({"algorithm": "monte_carlo", "reason": "Sensitivity to user-specified score uncertainty."})
        if req.has_resource_constraints and req.has_probabilities:
            match.append({"algorithm": "scenarios", "reason": "Expected-value or worst-case combinatorial decisions."})
    if not match:
        return {"status": "not_computable", "suggestions": [], "problem_type": req.problem_type,
                "missing_assumptions": ["Specify objectives, constraints, uncertainty, sequence, or service flow."]}
    return {"problem_type": req.problem_type, "suggestions": match,
            "notice": "Suggestions are heuristic only; the analyst must select and validate assumptions."}
