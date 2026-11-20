# Start here — EVIDORIX Codex handoff

This repository is a development handoff, not the final released product. It contains existing ClinOR v0.3 prototype code, synthetic tests, the approved EVIDORIX v2 visual identity, the editable 23-slide Slidev manual, and instructions for Codex to implement and publish.

## In Codex
1. Extract the ZIP file, open the extracted folder as the repository workspace (do not open the ZIP directly).
2. Read `AGENTS.md`, then `CODEX_MASTER_COMMAND.md` and `BRAND_IMPLEMENTATION.md`.
3. Paste the complete `CODEX_START_PROMPT.txt` in Codex and authorize GitHub connection if requested.
4. Expect genuine implementation, tests, UI screenshots, secret scanning and verified GitHub publication. The expected account is `asas2000034-spec`, repository slug `ClinOR-Engine`, public brand EVIDORIX.
5. If `ClinOR-Engine` already exists, retain its history; push a branch and PR rather than replacing content.

## Product requirements
- English-only interface and deliverables (en-US, LTR) across website, reports, LLM-generated analysis, OR results, README and brand materials.
- LLM provider interchangeable: local Ollama/LM Studio, optional explicit-consent cloud API.
- Cross-specialty evidence research with verifiable references and provenance.
- Multiple operations research methods with solver-appropriate validation and testing.
- No automated prescribing or claims of broad clinical validation.
- V2 Swiss Editorial brand only; do not revive the legacy glow/teal identity.

## Initial local prototype testing
```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q clinor
uvicorn clinor.api:app --reload
```

A previous test result is not a substitute for running tests in Codex's actual environment. Live LLM, network connectivity, security and UI validation must be reported independently.
