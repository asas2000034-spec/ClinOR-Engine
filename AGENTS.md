# AGENTS.md — EVIDORIX Codex Repo Rules

Read `CODEX_MASTER_COMMAND.md` first and execute its requirements, not merely summarize them.
Read `START_HERE.md`, `BRAND_IMPLEMENTATION.md` and the authority under `design/brand-v2/` before touching visual code.

## Repo invariants
- **English-only** platform (en-US, LTR): UI, LLM outputs, OR explanations, docs, all brand and GitHub materials. Preserve original source-language citations when necessary. No Arabic/bilingual UI.

- Public product name: **EVIDORIX**. Internal Python package: `clinor` (legacy compatibility).
- Canonical identity: `design/brand-v2/`; the existing `brand/` and CSS overlays are obsolete v1, not styling instructions.
- Cross-specialty research; no mandatory diabetes or other single-disease pathway.
- Local LLM via Ollama / OpenAI-compatible local endpoint, cloud optional by explicit per-request consent.
- Untrusted retrieval and LLM cannot approve guidelines, dosing, contraindications, clinical rules, clinical utilities, or patient-specific optimality.
- Separate evidence discovery, expert-reviewed clinical rule constraints, mathematical computation, and final professional review.
- Never fake citations, results, snapshots, test counts, live model connections, hospital savings, FDA/SFDA clearance, or validated decision coverage.
- Preserve API/back-end functionality through UI rebranding.

## Execution conventions
- Reproduce baseline tests and report findings; no fabricated green checks.
- Implement actual source code, tests, reproducible examples and docs.
- Prefer incremental commits and clear reversible changes.
- Never commit `.env`, secrets, real patient records, credentials, node_modules, generated caches or font binaries.
- Respect publisher copyright/terms; do not distribute guideline PDFs or full copyrighted guideline text.
- Review screen reader labeling, focus, contrast, and mobile/desktop layout.
- Publication only to verified account `asas2000034-spec`; existing target `ClinOR-Engine`. No force pushes or destructive histories.
- If publication/auth is blocked, finish all safe local work and report exact blocker.

## Done criteria
Working app + faithful EVIDORIX v2 brand + baseline/revised tests + validation limitations + documented local run + verified GitHub publication when permitted.
