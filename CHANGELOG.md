# EVIDORIX 0.3.1

Editorial workspace, provider consent checks, model-bound review records, evidence metadata, and session request IDs.

# Changelog

## 0.3.0 — Local-first language models

- Add native Ollama `/api/chat` adapter and OpenAI-compatible `/v1/chat/completions` adapter for LM Studio, llama.cpp and optional cloud services.
- Make local Ollama inference the default and remove reliance on `OPENAI_API_KEY` for the core AI workflow.
- Refactor evidence query planning and source-ID-limited synthesis into asynchronous, provider-agnostic calls.
- Add LLM explanations of deterministic OR method shortlist (solvers and reviewer-defined constraints remain independent).
- Add `/api/llm/status`, `/api/llm/check` and `/api/llm/method-advice`, live browser model status and testing controls.
- Require explicit server-side cloud opt-in, per-request cloud consent, and allowlisted local model hosts.
- Add `.env` loading, local Ollama Compose, configuration guide and transport-level tests.


## 0.2.0 — Operations Research Workbench

- Added typed OR engines: MCDA (TOPSIS/weighted sum), Pareto frontier, expected and maximin scenario MILP, Monte Carlo, Markov cohorts, dynamic programming, queueing theory and optional CP-SAT.
- Added model validation for scenario probability sums, state transition probabilities, duplicate IDs, resource and prerequisite constraints.
- Added deterministic, assumption-aware algorithm recommendation router.
- Added a UI workbench with editable synthetic JSON and executable API examples for every method.
- Added synthetic analytical reference and regression tests; extended GitHub Actions quality checks.
- Preserved condition-agnostic medical literature discovery and explicit human guideline review boundary.

## 0.1.0 — Initial prototype

- Cross-condition Europe PMC search, optional AI query planning/synthesis and guideline publisher search.
- SciPy mixed-integer binary selection with explicit restrictions.
- FastAPI, user interface, examples and test suite.
