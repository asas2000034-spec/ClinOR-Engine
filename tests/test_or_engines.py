"""Deterministic synthetic benchmarks; these do not measure clinical accuracy."""
import copy
import math

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from clinor.api import app
from clinor.or_engine import (
    cp_sat,
    dynamic_programming,
    markov,
    mcda,
    monte_carlo,
    pareto,
    queueing,
    scenario_optimization,
)
from clinor.or_engine.models import (
    CPSATRequest,
    DynamicRequest,
    MarkovRequest,
    MCDARequest,
    MonteCarloRequest,
    ParetoRequest,
    QueueingRequest,
    ScenarioRequest,
)

OPTIONS = [
    {"option_id": "A", "label": "Synthetic A", "benefit": 80, "burden": 40, "cost": 20},
    {"option_id": "B", "label": "Synthetic B", "benefit": 60, "burden": 20, "cost": 10},
    {"option_id": "C", "label": "Synthetic C", "benefit": 40, "burden": 50, "cost": 30},
]


def test_mcda_topsis_ranking_filters_excluded():
    sample = copy.deepcopy(OPTIONS)
    sample[0]["forbidden"] = True
    result = mcda(MCDARequest(options=sample))
    assert result.status == "completed"
    assert result.details["excluded"]["A"] == "forbidden"
    assert result.details["ranking"][0]["option_id"] == "B"
    assert all(0 <= row["score"] <= 1 for row in result.details["ranking"])


def test_mcda_weighted_and_constant_column():
    sample = copy.deepcopy(OPTIONS)
    for row in sample:
        row["cost"] = 3
    result = mcda(MCDARequest(options=sample, method="weighted_sum"))
    assert all(math.isfinite(row["score"]) for row in result.details["ranking"])


def test_mcda_handles_single_option():
    result = mcda(MCDARequest(options=[OPTIONS[0]]))
    assert result.details["ranking"][0]["score"] == pytest.approx(.5)


def test_mcda_requires_combination_excluded():
    sample = copy.deepcopy(OPTIONS)
    sample[0]["requires"] = ["B"]
    result = mcda(MCDARequest(options=sample))
    assert result.details["excluded"]["A"] == "requires_combination_not_modeled"


def test_pareto_correct_dominance():
    result = pareto(ParetoRequest(options=OPTIONS))
    assert result.details["pareto_frontier"] == ["A", "B"]
    assert result.details["dominated_by"]["C"] == ["A", "B"]


def scenario_input(strategy="maximin"):
    return {
        "strategy": strategy,
        "options": [
            {"option_id": "A", "label": "High variance", "benefit": 80, "burden": 0, "cost": 0},
            {"option_id": "B", "label": "Stable", "benefit": 60, "burden": 0, "cost": 0},
        ],
        "scenarios": [
            {"scenario_id": "favorable", "probability": 0.9, "payoffs": [
                {"option_id": "A", "benefit": 100, "burden": 0, "cost": 0},
                {"option_id": "B", "benefit": 60, "burden": 0, "cost": 0}]},
            {"scenario_id": "adverse", "probability": 0.1, "payoffs": [
                {"option_id": "A", "benefit": 0, "burden": 0, "cost": 0},
                {"option_id": "B", "benefit": 60, "burden": 0, "cost": 0}]},
        ],
    }


def test_scenario_expected_vs_maximin():
    expected = scenario_optimization(ScenarioRequest(**scenario_input("expected_value")))
    robust = scenario_optimization(ScenarioRequest(**scenario_input("maximin")))
    assert expected.status == "optimal" and expected.details["selected"] == ["A"]
    assert robust.status == "optimal" and robust.details["selected"] == ["B"]


def test_scenario_budget_always_enforced():
    data = scenario_input()
    data["budget"] = 5
    data["scenarios"][0]["payoffs"][0]["cost"] = 9
    data["scenarios"][1]["payoffs"][0]["cost"] = 2
    result = scenario_optimization(ScenarioRequest(**data))
    assert result.details["selected"] == ["B"]


def test_scenarios_no_relaxation_of_forbidden():
    data = scenario_input()
    for op in data["options"]:
        op["forbidden"] = True
    result = scenario_optimization(ScenarioRequest(**data))
    assert result.status == "infeasible"


def test_scenarios_bad_probabilities_rejected():
    data = scenario_input()
    data["scenarios"][0]["probability"] = .5
    with pytest.raises(ValidationError):
        ScenarioRequest(**data)


def test_scenarios_missing_payoff_rejected():
    data = scenario_input()
    data["scenarios"][0]["payoffs"].pop()
    with pytest.raises(ValidationError):
        ScenarioRequest(**data)


def test_monte_carlo_reproducible():
    data = {"seed": 123, "simulations": 1000, "options": [
        {"option_id": "A", "benefit_mean": 70, "benefit_sd": 10, "burden_mean": 20,
         "burden_sd": 4, "cost": 0},
        {"option_id": "B", "benefit_mean": 50, "benefit_sd": 0, "burden_mean": 20,
         "burden_sd": 0, "cost": 0},
    ]}
    r1 = monte_carlo(MonteCarloRequest(**data))
    r2 = monte_carlo(MonteCarloRequest(**data))
    assert r1.details == r2.details
    assert sum(row["probability_best_in_simulation"] for row in r1.details["ranking"]) == pytest.approx(1)


def markov_input():
    return {"state_names": ["well", "unwell"], "initial_distribution": [1, 0], "cycles": 2,
            "discount_rate": 0, "policies": [
                {"policy_id": "stable", "transition": [[1, 0], [0, 1]],
                 "reward_per_state": [10, 0], "cost_per_state": [0, 0]},
                {"policy_id": "declining", "transition": [[0, 1], [0, 1]],
                 "reward_per_state": [10, 0], "cost_per_state": [0, 0]},
            ]}


def test_markov_cohort_outcomes():
    result = markov(MarkovRequest(**markov_input()))
    assert result.details["policy_ranking"][0]["policy_id"] == "stable"
    assert result.details["policy_ranking"][0]["discounted_reward"] == 20
    assert result.details["policy_ranking"][1]["discounted_reward"] == 10


def test_markov_bad_transition_rejected():
    data = markov_input()
    data["policies"][0]["transition"][0] = [.3, .3]
    with pytest.raises(ValidationError):
        MarkovRequest(**data)


def dynamic_input():
    return {"states": ["ready", "done"], "initial_state": "ready", "horizon": 2,
            "discount_factor": 1, "actions": [
                {"state": "ready", "action": "finish", "immediate_reward": 3,
                 "outcomes": [{"next_state": "done", "probability": 1}]},
                {"state": "ready", "action": "wait", "immediate_reward": 0,
                 "outcomes": [{"next_state": "ready", "probability": 1}]},
                {"state": "done", "action": "stay", "immediate_reward": 2,
                 "outcomes": [{"next_state": "done", "probability": 1}]},
            ]}


def test_dynamic_programming_finite_horizon():
    result = dynamic_programming(DynamicRequest(**dynamic_input()))
    assert result.details["initial_state_value"] == pytest.approx(5)
    assert result.details["policy_by_period"][0]["actions_by_state"]["ready"] == "finish"


def test_dynamic_action_requires_probabilities():
    data = dynamic_input()
    data["actions"][0]["outcomes"][0]["probability"] = .9
    with pytest.raises(ValidationError):
        DynamicRequest(**data)


def test_queue_mm1_analytical():
    result = queueing(QueueingRequest(arrival_rate=1, service_rate_per_server=2, servers=1))
    assert result.details["utilization"] == pytest.approx(.5)
    assert result.details["probability_wait"] == pytest.approx(.5)
    assert result.details["expected_queue_time_in_rate_units"] == pytest.approx(.5)
    assert result.details["expected_system_time_in_rate_units"] == pytest.approx(1)


def test_queue_unstable():
    result = queueing(QueueingRequest(arrival_rate=2, service_rate_per_server=2, servers=1))
    assert result.status == "infeasible"


def test_queue_large_server_numerical_stability():
    result = queueing(QueueingRequest(arrival_rate=120, service_rate_per_server=2, servers=250))
    assert result.status == "completed"
    assert result.details["probability_wait"] >= 0


def test_clinical_gate_applies_to_every_engine():
    assert mcda(MCDARequest(options=OPTIONS, mode="clinical")).status == "review_required"
    assert pareto(ParetoRequest(options=OPTIONS, mode="clinical")).status == "review_required"
    assert markov(MarkovRequest(**markov_input(), mode="clinical")).status == "review_required"
    assert dynamic_programming(DynamicRequest(**dynamic_input(), mode="clinical")).status == "review_required"
    assert queueing(QueueingRequest(arrival_rate=1, service_rate_per_server=2,
                                    servers=1, mode="clinical")).status == "review_required"


def test_cp_sat_dependency_or_solution():
    req = CPSATRequest(options=OPTIONS, min_selections=1, max_selections=1)
    response = cp_sat(req)
    assert response.status in ("optimal", "unavailable")
    if response.status == "optimal":
        assert len(response.details["selected"]) == 1


def test_api_technique_listing_and_router():
    client = TestClient(app)
    output = client.get("/api/or/algorithms")
    assert output.status_code == 200
    assert len(output.json()["engines"]) >= 9
    recommendation = client.post("/api/or/recommend", json={"problem_type": "Synthetic choice",
        "has_multiple_criteria": True, "has_resource_constraints": True})
    assert recommendation.status_code == 200
    kinds = [item["algorithm"] for item in recommendation.json()["suggestions"]]
    assert "mcda" in kinds and "milp" in kinds


def test_api_mcda_and_validation():
    client = TestClient(app)
    response = client.post("/api/or/mcda", json={"options": OPTIONS})
    assert response.status_code == 200
    assert response.json()["algorithm"] == "mcda"
    assert client.post("/api/or/scenarios", json={"options": OPTIONS}).status_code == 422
    assert client.post("/api/or/mcda", json={"options": OPTIONS, "extra": "not allowed"}).status_code == 422
