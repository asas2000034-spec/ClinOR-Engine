# Architecture and boundaries

## Purpose
ClinOR is **a clinical evidence discovery and human-supervised optimization research framework**. It supports arbitrary clinical topics at the discovery layer. It is not a comprehensive disease knowledge graph and does not generate independently validated patient treatment recommendations.

## Trust boundary
1. Query planner may produce search terms. Treat generated strings as untrusted search inputs.
2. Europe PMC metadata and optional Brave or OpenAI web publisher search results are *candidates*, not up-to-date guideline endorsements.
3. LLM evidence briefs may summarize provided abstracts with citations; citation-ID checks are not entailment verification.
4. Clinicians and guideline maintainers must review full text, contraindications, temporal applicability, jurisdiction, patient preferences and evidence grading.
5. Only reviewer-supplied, auditable scores, probabilities, transitions and hard constraints reach the OR engines. The clinical-mode metadata gate is procedural, not proof of completed clinical validation.
6. The solver returns mathematical feasibility/optimality *relative to input model*, never verified clinical optimality.

## Security
- Source requests use fixed Europe PMC, Brave or OpenAI API hosts; arbitrary webpage fetching is not performed.
- Consent required before external topic search.
- No patient-data API and no EHR write access. Never provide identifiable patient data.
- Future real deployments require access controls, logs, retention rules, security assessment, bias analysis and local regulatory review.
- An untrusted abstract cannot change backend instructions or executable code.

## What makes this operations research?
The initial SciPy `milp` solves a binary optimization problem: maximize weighted reviewer-entered benefit, minus burden and cost, subject to treatment counts, absolute exclusion, pairwise incompatibility, prerequisites and budget. For overlapping treatments with complex interaction effects this additive demonstration is insufficient and must be replaced with clinically justified non-additive modeling.

## Evidence freshness and legal considerations
Article publication date, update date, jurisdiction, guideline version, recommendation strength and specialty organization must be independently confirmed before clinical use. Discovering copyrighted guidelines does not authorize mirroring them. Keep linking and metadata separate from content licensing.

## Evaluation roadmap
Test independently: retrieval recall against a reference corpus; publication classification accuracy; citation grounding; guideline review agreement; constraint execution; solver optimality; and end-to-end expert assessment across specialties. Track refusals/abstentions and missing data, not only apparent answer accuracy.

## Extended methods (v0.2+)

The new `clinor.or_engine` module exposes distinct Pydantic models and FastAPI endpoints for MCDA, Pareto analysis, scenario-based stochastic and robust mixed-integer optimization, seeded Monte Carlo analysis, cohort Markov models, finite-horizon dynamic programming, M/M/c queueing and optional CP-SAT. See [OR_METHODS.md](OR_METHODS.md) for exact assumptions and model limitations. The rule-based router does not fabricate clinical model parameters.

## LLM layer (v0.3)

`clinor.llm.LLMGateway` is the provider-neutral transport. Local Ollama uses native `/api/chat`, while LM Studio/other compatible providers use `/v1/chat/completions`. Cloud is disabled by default and requires both environment opt-in and per-request consent. `clinor.ai` uses this transport for query planning, citation-limited evidence summaries, and explanations of a deterministic OR router; **the mathematical solvers never import the LLM gateway**.

The user selects the mathematical solver and reviewer-validated inputs. LLM output is not used to change clinical option eligibility, hard constraints, scores, probabilities or transition matrices. This isolation is intentional until there is an independently validated guideline-to-rule compiler and clinical safety evaluation.

See [LLM_PROVIDERS.md](LLM_PROVIDERS.md).
