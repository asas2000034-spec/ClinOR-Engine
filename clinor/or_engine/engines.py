"""Multiple transparent operations-research engines with synthetic/reviewer inputs.

Algorithms do not infer treatment validity from retrieved publications. Their
mathematical outputs cannot establish comparative clinical effectiveness.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from math import exp, lgamma, log

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.special import logsumexp

from clinor.reviews import has_current_review

from .models import (
    DynamicRequest,
    MarkovRequest,
    MCDARequest,
    MonteCarloRequest,
    ORBase,
    ORResult,
    ParetoRequest,
    QueueingRequest,
    ScenarioRequest,
)

GENERAL_ASSUMPTIONS = [
    "Inputs, weights and restrictions are user/reviewer provided, not inferred from AI search.",
    "Mathematical ranking is not clinical evidence of treatment superiority.",
    "No prescribing, patient-data intake, EHR write-back or automatic clinical authorization.",
]


def _gate(req: ORBase, name: str) -> ORResult | None:
    if req.mode == "clinical" and not has_current_review(req):
        return ORResult(
            algorithm=name, status="review_required",
            summary="Clinical mode requires a versioned guideline review pack; no decision calculated.",
            assumptions=GENERAL_ASSUMPTIONS,
        )
    return None


def _output(req: ORBase, name: str, status: str, summary: str, details: dict,
            notes: list[str] | None = None) -> ORResult:
    return ORResult(
        algorithm=name, status=status, summary=summary, details=details,
        assumptions=GENERAL_ASSUMPTIONS + (notes or []),
        clinical_authorization=("requires_clinician_confirmation" if req.mode == "clinical"
                                else "not_authorized"),
    )


def _eligible_single(options, budget=None):
    # Prerequisites require selecting another option, so cannot be met in a single-choice ranking.
    accepted, excluded = [], {}
    for item in options:
        if item.forbidden:
            excluded[item.option_id] = "forbidden"
        elif budget is not None and item.cost > budget:
            excluded[item.option_id] = "over_budget"
        elif item.requires:
            excluded[item.option_id] = "requires_combination_not_modeled"
        else:
            accepted.append(item)
    return accepted, excluded


def mcda(req: MCDARequest) -> ORResult:
    if (denial := _gate(req, "mcda")):
        return denial
    options, excluded = _eligible_single(req.options, req.budget)
    if not options:
        return _output(req, "mcda", "infeasible", "No individually eligible options.",
                       {"excluded": excluded})
    values = np.array([[o.benefit, o.burden, o.cost] for o in options], dtype=float)
    weights = np.array([req.benefit_weight, req.burden_weight, req.cost_weight], dtype=float)
    weights /= sum(weights)
    if req.method == "topsis":
        norm = np.linalg.norm(values, axis=0)
        weighted = values / np.where(norm == 0, 1, norm) * weights
        ideal = np.array([np.max(weighted[:, 0]), np.min(weighted[:, 1]),
                          np.min(weighted[:, 2])])
        worst = np.array([np.min(weighted[:, 0]), np.max(weighted[:, 1]),
                          np.max(weighted[:, 2])])
        dbest = np.linalg.norm(weighted - ideal, axis=1)
        dworst = np.linalg.norm(weighted - worst, axis=1)
        denom = dbest + dworst
        scores = np.divide(dworst, denom, out=np.full(len(options), 0.5), where=denom > 0)
    else:
        # Directional min-max normalization makes scores comparable only within this candidate set.
        high_benefit = (values[:, 0] - values[:, 0].min())
        low_burden = (values[:, 1].max() - values[:, 1])
        low_cost = (values[:, 2].max() - values[:, 2])
        ranges = np.ptp(values, axis=0)
        cols = [x / ranges[i] if ranges[i] else np.full(len(options), 0.5)
                for i, x in enumerate([high_benefit, low_burden, low_cost])]
        scores = np.column_stack(cols) @ weights
    ranking = [{"option_id": o.option_id, "score": round(float(s), 6),
                "benefit": o.benefit, "burden": o.burden, "cost": o.cost}
               for o, s in zip(options, scores)]
    ranking.sort(key=lambda row: (-row["score"], row["option_id"]))
    return _output(req, "mcda", "completed", "Ranked individually eligible options.",
                   {"method": req.method, "ranking": ranking, "excluded": excluded},
                   ["Rank depends on criteria, weights and candidate set.",
                    "TOPSIS/weighted-sum scores are not outcome probabilities or validated utilities."])


def pareto(req: ParetoRequest) -> ORResult:
    if (denial := _gate(req, "pareto")):
        return denial
    options, excluded = _eligible_single(req.options, req.budget)
    if not options:
        return _output(req, "pareto", "infeasible", "No individually eligible options.",
                       {"excluded": excluded})
    nondominated = []
    dominated = {}
    for a in options:
        dominators = [b.option_id for b in options if b.option_id != a.option_id
                      and b.benefit >= a.benefit and b.burden <= a.burden
                      and b.cost <= a.cost and
                      (b.benefit > a.benefit or b.burden < a.burden or b.cost < a.cost)]
        if dominators:
            dominated[a.option_id] = sorted(dominators)
        else:
            nondominated.append(a.option_id)
    return _output(req, "pareto", "completed", "Computed nondominated single-choice alternatives.",
                   {"pareto_frontier": sorted(nondominated), "dominated_by": dominated,
                    "excluded": excluded},
                   ["Dominance uses benefit ↑, burden ↓, cost ↓; no weights assumed.",
                    "Complex treatment combinations and interactions are not evaluated."])


def scenario_optimization(req: ScenarioRequest) -> ORResult:
    if (denial := _gate(req, "scenarios")):
        return denial
    n = len(req.options)
    k = len(req.scenarios)
    positions = {o.option_id: i for i, o in enumerate(req.options)}
    utility = np.zeros((k, n), dtype=float)
    cost = np.zeros((k, n), dtype=float)
    for si, scenario in enumerate(req.scenarios):
        for payoff in scenario.payoffs:
            i = positions[payoff.option_id]
            utility[si, i] = (req.benefit_weight * payoff.benefit
                               - req.burden_weight * payoff.burden
                               - req.cost_weight * payoff.cost)
            cost[si, i] = payoff.cost
    probs = np.array([s.probability for s in req.scenarios])
    robust = req.strategy == "maximin"
    size = n + int(robust)
    rows, lo, hi = [], [], []

    def add(coeff, lower, upper):
        row = np.zeros(size)
        row[:len(coeff)] = coeff
        rows.append(row)
        lo.append(lower)
        hi.append(upper)

    add(np.ones(n), req.min_selections, req.max_selections)
    if req.budget is not None:
        for si in range(k):
            add(cost[si], -np.inf, req.budget)  # scenario-wise hard budget
    for i, option in enumerate(req.options):
        for name in option.incompatible_with:
            row = np.zeros(n)
            row[i] = row[positions[name]] = 1
            add(row, -np.inf, 1)
        for name in option.requires:
            row = np.zeros(n)
            row[i] = 1
            row[positions[name]] = -1
            add(row, -np.inf, 0)
    objective = np.zeros(size)
    lb = np.zeros(size)
    ub = np.array([0.0 if op.forbidden else 1.0 for op in req.options]
                  + ([1.0] if robust else []), dtype=float)
    if robust:
        # Bound scenario net scores (even for empty selection) to keep MILP numerically bounded.
        magnitude = float(np.max(np.sum(np.abs(utility), axis=1))) + 1.0
        lb[-1], ub[-1] = -magnitude, magnitude
        objective[-1] = -1
        for si in range(k):
            row = np.zeros(size)
            row[:n] = -utility[si]
            row[-1] = 1
            rows.append(row)
            lo.append(-np.inf)
            hi.append(0.0)
    else:
        objective[:n] = -(probs @ utility)
    try:
        result = milp(c=objective, integrality=np.array([1] * n + [0] * int(robust)),
                      bounds=Bounds(lb, ub),
                      constraints=LinearConstraint(np.array(rows), np.array(lo), np.array(hi)),
                      options={"time_limit": 10})
    except (ValueError, RuntimeError, OverflowError):
        return _output(req, "scenarios", "error", "Solver failed; review data scaling.", {})
    if result.x is None:
        status = "infeasible" if result.status == 2 else "error"
        return _output(req, "scenarios", status,
                       "No feasible solution under all supplied hard constraints."
                       if status == "infeasible" else "Solver did not return a solution.",
                       {"solver_status": int(result.status)})
    chosen = (result.x[:n] > 0.5).astype(float)
    per_scenario = [{"scenario_id": s.scenario_id, "probability": s.probability,
                     "net_score": round(float(utility[j] @ chosen), 5),
                     "total_cost": round(float(cost[j] @ chosen), 5)}
                    for j, s in enumerate(req.scenarios)]
    status = "optimal" if result.status == 0 else "feasible"
    return _output(req, "scenarios", status,
                   "Optimized a feasible combination across all specified scenarios.",
                   {"strategy": req.strategy,
                    "selected": [o.option_id for o, x in zip(req.options, chosen) if x],
                    "expected_net_score": round(float(probs @ utility @ chosen), 5),
                    "worst_net_score": round(float(np.min(utility @ chosen)), 5),
                    "scenarios": per_scenario, "solver_status": int(result.status)},
                   ["Scenarios and probabilities are hypothetical/reviewer-supplied.",
                    "The budget (if provided) must hold in every scenario; hard exclusions are never relaxed."])


def monte_carlo(req: MonteCarloRequest) -> ORResult:
    if (denial := _gate(req, "monte_carlo")):
        return denial
    options = [o for o in req.options if not o.forbidden]
    if not options:
        return _output(req, "monte_carlo", "infeasible", "All options are forbidden.", {})
    rng = np.random.default_rng(req.seed)
    utility = np.zeros((req.simulations, len(options)))
    for i, o in enumerate(options):
        benefits = np.clip(rng.normal(o.benefit_mean, o.benefit_sd, req.simulations), 0, 100)
        burdens = np.clip(rng.normal(o.burden_mean, o.burden_sd, req.simulations), 0, 100)
        utility[:, i] = (req.benefit_weight * benefits - req.burden_weight * burdens
                         - req.cost_weight * o.cost)
    winners = np.argmax(utility, axis=1)  # ties resolve deterministically by input order
    rows = []
    for i, o in enumerate(options):
        rows.append({"option_id": o.option_id,
                     "mean_net_score": round(float(utility[:, i].mean()), 4),
                     "p05_net_score": round(float(np.quantile(utility[:, i], .05)), 4),
                     "p95_net_score": round(float(np.quantile(utility[:, i], .95)), 4),
                     "probability_best_in_simulation": round(float(np.mean(winners == i)), 5),
                     "probability_negative_net_score": round(float(np.mean(utility[:, i] < 0)), 5)})
    rows.sort(key=lambda x: (-x["mean_net_score"], x["option_id"]))
    return _output(req, "monte_carlo", "completed", "Simulated user-defined uncertainty in single-choice option scores.",
                   {"seed": req.seed, "draws": req.simulations, "ranking": rows},
                   ["Normal score distributions were assumed then clipped to [0,100].",
                    "Simulated probability of a highest score is NOT a probability of clinical effectiveness.",
                    "Correlation between outcomes and uncertainty in costs are not modeled."])


def markov(req: MarkovRequest) -> ORResult:
    if (denial := _gate(req, "markov")):
        return denial
    out = []
    for policy in req.policies:
        distribution = np.array(req.initial_distribution, dtype=float)
        transition = np.array(policy.transition, dtype=float)
        reward = np.array(policy.reward_per_state, dtype=float)
        cost = np.array(policy.cost_per_state, dtype=float)
        total_reward = 0.0
        total_cost = 0.0
        trajectory = [{"cycle": 0, "distribution": [round(float(x), 7) for x in distribution]}]
        for cycle in range(req.cycles):
            discount = (1 + req.discount_rate) ** (-cycle)
            total_reward += discount * float(distribution @ reward)
            total_cost += discount * float(distribution @ cost)
            distribution = distribution @ transition
            if cycle < 9 or cycle == req.cycles - 1:
                trajectory.append({"cycle": cycle + 1,
                                   "distribution": [round(float(x), 7) for x in distribution]})
        out.append({"policy_id": policy.policy_id,
                    "discounted_reward": round(total_reward, 5),
                    "discounted_cost": round(total_cost, 5),
                    "net_score": round(total_reward - req.cost_weight * total_cost, 5),
                    "trajectory_sample": trajectory})
    out.sort(key=lambda x: (-x["net_score"], x["policy_id"]))
    return _output(req, "markov", "completed", "Computed finite-cycle cohort Markov model outcomes.",
                   {"policy_ranking": out, "cycles": req.cycles,
                    "state_names": req.state_names},
                   ["State rewards are arbitrary input units, NOT automatically QALYs.",
                    "Time-homogeneous state transitions and fixed per-cycle rewards are assumed.",
                    "No probabilistic sensitivity analysis or empirical calibration is performed."])


def dynamic_programming(req: DynamicRequest) -> ORResult:
    if (denial := _gate(req, "dynamic_programming")):
        return denial
    options = defaultdict(list)
    for action in req.actions:
        options[action.state].append(action)
    values = {state: 0.0 for state in req.states}
    backwards = []
    for _ in range(req.horizon):
        next_values = {}
        decisions = {}
        for state in req.states:
            eligible = options[state]
            # Tie-breaking deterministic via sorted action names.
            optimal = max(sorted(eligible, key=lambda a: a.action),
                          key=lambda a: a.immediate_reward + req.discount_factor * sum(
                              outcome.probability * values[outcome.next_state]
                              for outcome in a.outcomes))
            next_values[state] = optimal.immediate_reward + req.discount_factor * sum(
                outcome.probability * values[outcome.next_state] for outcome in optimal.outcomes)
            decisions[state] = optimal.action
        values = next_values
        backwards.append(decisions)
    policy = list(reversed(backwards))
    return _output(req, "dynamic_programming", "optimal", "Solved finite-horizon expected-reward decision process.",
                   {"initial_state": req.initial_state,
                    "initial_state_value": round(values[req.initial_state], 6),
                    "policy_by_period": [{"period": i + 1, "actions_by_state": actions}
                                         for i, actions in enumerate(policy)]},
                   ["Finite-horizon fully observed Markov decision process.",
                    "Actions, transition probabilities and rewards are supplied, not learned.",
                    "The objective is expected cumulative user-defined reward."])


def queueing(req: QueueingRequest) -> ORResult:
    if (denial := _gate(req, "queueing")):
        return denial
    lam, mu, c = req.arrival_rate, req.service_rate_per_server, req.servers
    utilization = lam / (c * mu)
    if utilization >= 1:
        return _output(req, "queueing", "infeasible", "M/M/c queue has no stable steady state at these rates.",
                       {"utilization": round(utilization, 6)})
    a = lam / mu
    logs = [k * log(a) - lgamma(k + 1) for k in range(c)]
    tail = c * log(a) - lgamma(c + 1) - log(1 - utilization)
    normalizer = logsumexp(logs + [tail])
    probability_wait = exp(tail - normalizer)
    wq = probability_wait / (c * mu - lam)
    w = wq + 1 / mu
    return _output(req, "queueing", "completed", "Computed stable M/M/c queue performance.",
                   {"servers": c, "utilization": round(utilization, 6),
                    "probability_wait": round(probability_wait, 6),
                    "expected_queue_time_in_rate_units": round(wq, 6),
                    "expected_system_time_in_rate_units": round(w, 6),
                    "expected_queue_length": round(lam * wq, 6), "rate_unit": req.rate_unit},
                   ["Assumes Poisson arrivals, exponential independent service and FCFS, infinite capacity.",
                    "Rate unit must be the same for arrivals and service.",
                    "Operational service analysis, not treatment selection."])


def cp_sat(req) -> ORResult:
    """Optional OR-Tools binary CP-SAT, with explicit input precision contract."""
    if (denial := _gate(req, "cp_sat")):
        return denial
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return _output(req, "cp_sat", "unavailable",
                       "Install the optional solver: pip install -e '.[cp]'", {})

    def exact_fixed_point(number: float | Decimal, scale: int = 1000) -> int:
        decimal = Decimal(str(number)) * Decimal(scale)
        if decimal != decimal.to_integral_value() or abs(decimal) > 10**15:
            raise ValueError("CP-SAT inputs require at most 3 input decimal places")
        return int(decimal)

    try:
        budget = exact_fixed_point(req.budget) if req.budget is not None else None
        costs = [exact_fixed_point(op.cost) for op in req.options]
        # Three-decimal weights times three-decimal scores need 10^6 scale.
        coeffs = [exact_fixed_point(
            Decimal(str(req.benefit_weight)) * Decimal(str(op.benefit))
            - Decimal(str(req.burden_weight)) * Decimal(str(op.burden))
            - Decimal(str(req.cost_weight)) * Decimal(str(op.cost)),
            1_000_000) for op in req.options]
    except (ValueError, InvalidOperation):
        return _output(req, "cp_sat", "error",
                       "Precision check failed; no coefficients were silently rounded.", {})
    model = cp_model.CpModel()
    x = {op.option_id: model.new_bool_var(op.option_id) for op in req.options}
    model.add(sum(x.values()) >= req.min_selections)
    model.add(sum(x.values()) <= req.max_selections)
    if budget is not None:
        model.add(sum(cost * x[op.option_id] for op, cost in zip(req.options, costs)) <= budget)
    for op in req.options:
        if op.forbidden:
            model.add(x[op.option_id] == 0)
        for other in op.incompatible_with:
            model.add(x[op.option_id] + x[other] <= 1)
        for prerequisite in op.requires:
            model.add_implication(x[op.option_id], x[prerequisite])
    model.maximize(sum(value * x[op.option_id] for op, value in zip(req.options, coeffs)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    if status == cp_model.INFEASIBLE:
        return _output(req, "cp_sat", "infeasible", "No feasible option combination.", {})
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return _output(req, "cp_sat", "error", "Solver did not produce a valid incumbent.",
                       {"solver_status": int(status)})
    selected = [op.option_id for op in req.options if solver.value(x[op.option_id])]
    return _output(req, "cp_sat", "optimal" if status == cp_model.OPTIMAL else "feasible",
                   "Solved discrete combination constraints with CP-SAT.",
                   {"selected": selected, "net_score": solver.objective_value / 1_000_000,
                    "solver_status": int(status)},
                   ["CP-SAT uses 0.001 input precision and 0.000001 objective precision, with no rounding.",
                    "Independent from the SciPy MILP solver; only binary decisions are supported."])
