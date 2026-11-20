# ClinOR Engine — Portfolio case study

## One-line description
An open-source, condition-agnostic clinical evidence research pipeline with optional AI literature search planning, reference-linked synthesis, and a multi-engine operations research workbench for explicitly reviewed or fictional model inputs.

## The problem
Clinical guidance is distributed across specialty societies, journals and national publishers. Retrieving the right evidence, tracking provenance and evaluating constrained treatment alternatives are different tasks often conflated in AI chat applications.

## The approach
I separated three concerns: (1) retrieve scientific records from actual indexes, with optional AI query planning and guideline-page web search, (2) summarize *only the retrieved record metadata and abstracts* with source IDs and stated uncertainty, and (3) optimize clinician-authored candidate options using a transparent mathematical model, hard exclusions and resource constraints.

## Technical implementation (v0.2 prototype)
- Designed a condition-agnostic source-retrieval API and web interface.
- Implemented a real Europe PMC literature connector and optional Brave Web Search connector.
- Added configurable OpenAI-based literature query planning and limited, cited synthesis.
- Implemented SciPy MILP, option-ranking MCDA, Pareto frontier, robust and stochastic scenario MILP, seeded Monte Carlo, cohort Markov, finite-horizon dynamic programming, and M/M/c queueing; integrated optional OR-Tools CP-SAT.
- Established a basic human-review metadata gate; clinical effectiveness and correctness have **not** been validated.
- Added 36 automated offline tests, typed APIs, synthetic examples, GitHub Actions, a developer workbench, and explicit research/clinical safety boundaries.

## Current results
The codebase passes 36 automated offline tests spanning solver properties, analytical reference cases, input schemas and generic evidence discovery. **No patient outcome improvements, clinical accuracy rates, or real-world hospital cost savings are claimed.** Live third-party searches and LLM responses depend on configured service access and have not been independently validated in this version.

## What I would evaluate next
- Guideline search recall/precision on independently adjudicated cross-specialty cases.
- Reliability of metadata links, guideline version identification, supersession and national applicability.
- Citation entailment and rates of unsupported LLM statements.
- Agreement of machine-readable rule packs with expert guideline reviewers.
- Solver validity for complex combinations, including interactions and multiple objectives.
- End-to-end comparative assessment against clinician-reviewed baselines.

## Links
The GitHub URL can be added once the project is published. Do not claim a deployment, publication or adoption that has not happened.
