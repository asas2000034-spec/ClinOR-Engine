"""Strict contracts for research-grade operations research demonstrations.

Every score, probability, transition or constraint is PROVIDED by the caller.
No evidence-search output is silently transformed into a clinical decision model.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from clinor.schemas import GuidelineApproval, TreatmentOption


class ORBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["sandbox", "clinical"] = "sandbox"
    guideline_approval: GuidelineApproval | None = None


class OptionSet(ORBase):
    options: list[TreatmentOption] = Field(min_length=1, max_length=60)

    @model_validator(mode="after")
    def check_options(self):
        ids = [item.option_id for item in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate option_id")
        for item in self.options:
            if (set(item.requires) | set(item.incompatible_with)) - set(ids):
                raise ValueError("Unknown option_id in requires or incompatible_with")
            if item.option_id in item.requires or item.option_id in item.incompatible_with:
                raise ValueError("Options cannot reference themselves")
        return self


class MCDARequest(OptionSet):
    method: Literal["topsis", "weighted_sum"] = "topsis"
    benefit_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    burden_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    cost_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    budget: float | None = Field(default=None, ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def weights_valid(self):
        if not any([self.benefit_weight, self.burden_weight, self.cost_weight]):
            raise ValueError("At least one criterion weight must be positive")
        return self


class ParetoRequest(OptionSet):
    budget: float | None = Field(default=None, ge=0, allow_inf_nan=False)


class ScenarioPayoff(BaseModel):
    model_config = ConfigDict(extra="forbid")
    option_id: str
    benefit: float = Field(ge=0, le=100, allow_inf_nan=False)
    burden: float = Field(ge=0, le=100, allow_inf_nan=False)
    cost: float = Field(ge=0, allow_inf_nan=False)


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario_id: str = Field(min_length=1, max_length=60)
    probability: float = Field(ge=0, le=1, allow_inf_nan=False)
    payoffs: list[ScenarioPayoff] = Field(min_length=1, max_length=60)


class ScenarioRequest(OptionSet):
    strategy: Literal["expected_value", "maximin"] = "maximin"
    scenarios: list[Scenario] = Field(min_length=2, max_length=25)
    min_selections: int = Field(default=1, ge=0, le=60)
    max_selections: int = Field(default=1, ge=1, le=60)
    budget: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    benefit_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    burden_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    cost_weight: float = Field(default=0, ge=0, le=100, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_scenarios(self):
        expected = {item.option_id for item in self.options}
        names = [s.scenario_id for s in self.scenarios]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate scenario_id")
        if abs(sum(s.probability for s in self.scenarios) - 1) > 1e-7:
            raise ValueError("Scenario probabilities must sum to 1")
        if self.min_selections > self.max_selections:
            raise ValueError("min_selections cannot exceed max_selections")
        if not any([self.benefit_weight, self.burden_weight, self.cost_weight]):
            raise ValueError("At least one criterion weight must be positive")
        for scenario in self.scenarios:
            ids = [payoff.option_id for payoff in scenario.payoffs]
            if set(ids) != expected or len(ids) != len(expected):
                raise ValueError("Every scenario must define one payoff for each option")
        return self


class UncertainOption(BaseModel):
    model_config = ConfigDict(extra="forbid")
    option_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    benefit_mean: float = Field(ge=0, le=100, allow_inf_nan=False)
    benefit_sd: float = Field(ge=0, le=100, allow_inf_nan=False)
    burden_mean: float = Field(ge=0, le=100, allow_inf_nan=False)
    burden_sd: float = Field(ge=0, le=100, allow_inf_nan=False)
    cost: float = Field(ge=0, allow_inf_nan=False)
    forbidden: bool = False


class MonteCarloRequest(ORBase):
    options: list[UncertainOption] = Field(min_length=2, max_length=50)
    simulations: int = Field(default=2000, ge=100, le=10000)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)
    benefit_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    burden_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    cost_weight: float = Field(default=0, ge=0, le=100, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_inputs(self):
        ids = [o.option_id for o in self.options]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate option_id")
        if not any([self.benefit_weight, self.burden_weight, self.cost_weight]):
            raise ValueError("At least one criterion weight must be positive")
        return self


class MarkovPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str = Field(min_length=1, max_length=50)
    transition: list[list[float]] = Field(min_length=2, max_length=15)
    reward_per_state: list[float] = Field(min_length=2, max_length=15)
    cost_per_state: list[float] = Field(min_length=2, max_length=15)


class MarkovRequest(ORBase):
    state_names: list[str] = Field(min_length=2, max_length=15)
    initial_distribution: list[float] = Field(min_length=2, max_length=15)
    policies: list[MarkovPolicy] = Field(min_length=2, max_length=12)
    cycles: int = Field(default=20, ge=1, le=150)
    discount_rate: float = Field(default=0.03, ge=0, le=1, allow_inf_nan=False)
    cost_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_dimensions(self):
        n = len(self.state_names)
        if len(set(self.state_names)) != n or len(self.initial_distribution) != n:
            raise ValueError("State names must be unique and match initial_distribution")
        if not _distribution(self.initial_distribution):
            raise ValueError("Initial probabilities must be finite, nonnegative and sum to 1")
        if len({p.policy_id for p in self.policies}) != len(self.policies):
            raise ValueError("Duplicate policy_id")
        for policy in self.policies:
            if len(policy.transition) != n or len(policy.reward_per_state) != n or len(policy.cost_per_state) != n:
                raise ValueError("Policy dimensions must match states")
            if not all(len(row) == n and _distribution(row) for row in policy.transition):
                raise ValueError("Every Markov transition row must sum to 1")
            if not all(_finite(x) for x in policy.reward_per_state + policy.cost_per_state):
                raise ValueError("Nonfinite reward/cost not allowed")
            if any(x < 0 for x in policy.cost_per_state):
                raise ValueError("Costs cannot be negative")
        return self


class TransitionOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")
    next_state: str
    probability: float = Field(ge=0, le=1, allow_inf_nan=False)


class StateAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    state: str
    action: str
    immediate_reward: float = Field(allow_inf_nan=False)
    outcomes: list[TransitionOutcome] = Field(min_length=1, max_length=25)


class DynamicRequest(ORBase):
    states: list[str] = Field(min_length=1, max_length=25)
    initial_state: str
    actions: list[StateAction] = Field(min_length=1, max_length=200)
    horizon: int = Field(default=8, ge=1, le=100)
    discount_factor: float = Field(default=0.95, ge=0, le=1, allow_inf_nan=False)

    @model_validator(mode="after")
    def check_actions(self):
        state_set = set(self.states)
        if len(state_set) != len(self.states) or self.initial_state not in state_set:
            raise ValueError("Unique states and a valid initial_state required")
        seen: set[tuple[str, str]] = set()
        for a in self.actions:
            if a.state not in state_set or any(o.next_state not in state_set for o in a.outcomes):
                raise ValueError("Transition references an unknown state")
            if not _distribution([o.probability for o in a.outcomes]):
                raise ValueError("Action transition probabilities must sum to 1")
            if len({o.next_state for o in a.outcomes}) != len(a.outcomes):
                raise ValueError("Duplicate destination state in action")
            if (a.state, a.action) in seen:
                raise ValueError("Duplicate state-action pair")
            seen.add((a.state, a.action))
        if any(not any(a.state == state for a in self.actions) for state in self.states):
            raise ValueError("Every state requires an available action")
        return self


class QueueingRequest(ORBase):
    arrival_rate: float = Field(gt=0, le=100000, allow_inf_nan=False)
    service_rate_per_server: float = Field(gt=0, le=100000, allow_inf_nan=False)
    servers: int = Field(ge=1, le=250)
    rate_unit: str = Field(default="hour", min_length=1, max_length=30)


class ORResult(BaseModel):
    algorithm: str
    status: Literal["completed", "optimal", "feasible", "infeasible", "review_required", "unavailable", "error"]
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    clinical_authorization: Literal["not_authorized", "requires_clinician_confirmation"] = "not_authorized"


def _finite(value: float) -> bool:
    import math
    return math.isfinite(value)


def _distribution(values: list[float]) -> bool:
    return all(_finite(x) and x >= 0 for x in values) and abs(sum(values) - 1) <= 1e-7

class CPSATRequest(OptionSet):
    min_selections: int = Field(default=1, ge=0, le=60)
    max_selections: int = Field(default=1, ge=1, le=60)
    budget: float | None = Field(default=None, ge=0, le=1_000_000_000, allow_inf_nan=False)
    benefit_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    burden_weight: float = Field(default=1, ge=0, le=100, allow_inf_nan=False)
    cost_weight: float = Field(default=0, ge=0, le=100, allow_inf_nan=False)

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min_selections > self.max_selections:
            raise ValueError("min_selections cannot exceed max_selections")
        if not any([self.benefit_weight, self.burden_weight, self.cost_weight]):
            raise ValueError("At least one criterion weight must be positive")
        return self
