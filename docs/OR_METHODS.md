# Operations Research Methods — Mathematical Contracts

All examples use fictional options and researcher-supplied scores. No objective value here establishes clinical benefit or patient suitability. This document describes *implemented* behavior, not a clinical indication.

## MILP (binary treatment *option* selection)

Legacy `/api/optimize` implements binary selection with benefit, burden and cost weights, count limits, forbidden candidates, pairwise incompatibility, prerequisites and an optional budget. Uses SciPy's HiGHS-backed `milp`; see [OPTIMIZATION_MODEL.md](OPTIMIZATION_MODEL.md).

## CP-SAT (optional)

`/api/or/cp-sat` models the same basic binary constraints with OR-Tools Boolean variables, implication, and integer objective coefficients. Unlike MILP, CP-SAT requires an integer representation: ClinOR accepts up to 3 decimal places in input costs/scores/weights, multiplies costs by 1,000 and weighted score coefficients by 1,000,000, **rejects** values that cannot be represented exactly, and never silently rounds a safety-critical budget. `status=unavailable` if `ortools` is not installed.

## MCDA — TOPSIS and weighted sums

`/api/or/mcda` compares **single** eligible options, not joint combinations. Explicitly excluded options and options that require another option are omitted. Budget is a single-option cap. Benefit is maximized, burden and cost minimized. TOPSIS computes weighted normalized closeness to an ideal vector; weighted sum rescales columns to the [0,1] observed range and scores by normalized weights. Results depend on the provided candidate set and weights. Score is **not** probability of treatment success.

## Pareto dominance

`/api/or/pareto` retains option `i` if no other eligible single option has benefit >=, burden <=, cost <= and strictly improves at least one dimension. It reports which options dominate an excluded alternative. It does not solve complex combinations; a nondominated alternative is **not** clinically indicated.

## Stochastic and robust scenario optimization

`/api/or/scenarios` consumes explicit scenario probabilities, per-option payoff vectors and the same hard constraints as the binary MILP:

- `expected_value`: maximize `sum_s p[s] * sum_i utility[s,i] * x[i]`.
- `maximin`: maximize auxiliary `t`, subject to `t <= sum_i utility[s,i] * x[i]` for **each** scenario `s`.
- Scenario probabilities must sum to 1, including in maximin mode (for consistent reporting).
- Any supplied financial budget is enforced **under every scenario**, even in expected-value mode; no unsafe relaxation occurs.
- User-defined additive utilities ignore nonadditive effects, interactions and evidence certainty.

A solver may terminate with a merely feasible incumbent. The reported `status` differentiates this from proof of optimality.

## Monte Carlo

`/api/or/monte-carlo` draws seeded *independent* normal benefits/burdens per option, clips to [0,100], computes the specified weighted score and reports mean, 5th/95th percentile and fraction of simulations where a candidate ranks first. These are frequencies **under the supplied model**, not confidence that a medication will work. Correlations, model structure uncertainty, alternative distributions and cost uncertainty are outside current scope.

## Cohort Markov state-transition model

`/api/or/markov` evolves cohort distribution `p[t+1] = p[t] P` over finite cycles. For each policy, rewards and costs accrue from current state at cycle t, discounted by `(1+r)^(-t)`. Results include per-policy accumulated rewards, costs and net score, with a sampled state trajectory. Transition matrices are time-homogeneous row-stochastic and supplied by the caller. Rewards have arbitrary units: **do not call them QALYs** unless supported by a validated utility measure.

## Dynamic programming / finite-horizon MDP

`/api/or/dynamic-programming` performs backward induction using

`V[t,s] = max_a [ r(s,a) + gamma * sum_s' P(s'|s,a) * V[t+1,s'] ]`,

with `V[horizon,s]=0`. States, actions, rewards and probabilities are supplied. The output is a policy by state and period. It assumes full state observability and known transition probabilities; it does not learn an MDP from patient data.

## M/M/c queueing (operational, not therapeutic)

`/api/or/queueing` returns Erlang C estimates for a single-class steady-state queue with `c` identical servers, Poisson arrival rate lambda, exponential service rate mu per server, FCFS and infinite queue capacity. Utilization `rho=lambda/(c*mu)`. If `rho>=1` the steady-state queue is unstable and no finite waiting-time estimate is returned. Estimates are computed with log-domain arithmetic for numerical stability.

## Routing, verification and future work

`POST /api/or/recommend` is *not* autonomous optimization. It provides a deterministic shortlist based on explicit flags, which an analyst must review. The broader OR field also contains network flows, discrete-event simulation, nonlinear optimization, continuous LP, game theory and control; they are **not** all implemented here.

Every OR algorithm must have property/unit tests, structured validation, explicit assumptions, and independent methodological and clinical review before expanding into regulated settings.
