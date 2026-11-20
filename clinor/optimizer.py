"""Reviewer-supplied, constrained binary optimization (not an autonomous prescribing tool)."""
from __future__ import annotations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from .reviews import has_current_review
from .schemas import OptimizeRequest, OptimizeResponse


def optimize(req: OptimizeRequest) -> OptimizeResponse:
    if req.mode == "clinical" and not has_current_review(req):
        return OptimizeResponse(status="review_required", explanation=(
            "Clinical mode requires a human-reviewed, versioned guideline pack before optimization. "
            "This engine cannot determine clinical eligibility from raw AI search results."))
    n = len(req.options)
    positions = {op.option_id: i for i, op in enumerate(req.options)}
    # Objective is a transparent reviewer-defined utility; it is NOT medical utility or QALY.
    utility = np.array([req.benefit_weight * op.benefit - req.burden_weight * op.burden
                        - req.cost_weight * op.cost for op in req.options], dtype=float)
    rows = []
    lower = []
    upper = []

    def row_constraint(row: np.ndarray, lo: float, hi: float) -> None:
        rows.append(row)
        lower.append(lo)
        upper.append(hi)

    row_constraint(np.ones(n), req.min_selections, req.max_selections)
    if req.budget is not None:
        row_constraint(np.array([op.cost for op in req.options]), -np.inf, req.budget)
    for i, option in enumerate(req.options):
        for name in option.incompatible_with:
            j = positions[name]
            row = np.zeros(n)
            row[i] = row[j] = 1
            row_constraint(row, -np.inf, 1)
        for name in option.requires:
            j = positions[name]
            row = np.zeros(n)
            row[i], row[j] = 1, -1
            row_constraint(row, -np.inf, 0)
    upper_bounds = np.array([0.0 if op.forbidden else 1.0 for op in req.options])
    try:
        result = milp(
            c=-utility, integrality=np.ones(n),
            bounds=Bounds(np.zeros(n), upper_bounds),
            constraints=LinearConstraint(np.array(rows), np.array(lower), np.array(upper)),
            options={"time_limit": 10},
        )
    except (ValueError, RuntimeError) as exc:
        return OptimizeResponse(status="solver_error", explanation=f"Solver issue: {type(exc).__name__}")
    if result.status != 2 and (result.x is None or result.status not in (0, 1)):
        return OptimizeResponse(status="solver_error", explanation="Solver stopped without a verified feasible solution.")
    if result.status == 2:
        return OptimizeResponse(status="infeasible", explanation=(
            "No feasible option combination exists under the supplied constraints. Review restrictions; "
            "the system does not relax clinical exclusions."))
    selected = [req.options[i].option_id for i, x in enumerate(result.x) if x > 0.5]
    status = "optimal" if result.status == 0 else "feasible"
    return OptimizeResponse(
        status=status, selected=selected, objective=round(float(utility @ np.rint(result.x)), 4),
        explanation="Optimized reviewer-entered scores with explicit selection and resource constraints.",
        clinical_authorization="requires_clinician_confirmation" if req.mode == "clinical"
        else "not_authorized",
        caveats=["Scores and restrictions are user-supplied and not clinically validated by this solver.",
                 "No automatic patient treatment, medication orders, or EHR write-back.",
                 "An optimal mathematical result is not proof of clinical superiority."],
    )
