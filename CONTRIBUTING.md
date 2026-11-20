# Contributing

We welcome issues, literature retrieval adapters, optimization formulations, accessibility fixes, and tests.

1. Open an issue describing the scope and scientific rationale.
2. Use topic-agnostic APIs; avoid silently hardcoding a disease-specific algorithm into the core.
3. Include executable tests, source attribution, versioning and limitations.
4. No patient-identifiable data, credentials, proprietary guideline full texts, or unlicensed terminology databases in pull requests.
5. All proposed clinical rules require a documented human clinical review and cannot be merged as automatically approved by an LLM.

Run `python -m pytest -q` and `python -m compileall -q clinor` before opening a PR.
