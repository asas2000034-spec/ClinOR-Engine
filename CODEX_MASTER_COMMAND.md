# EVIDORIX — CODEX MASTER ENGINEERING & PUBLISHING COMMAND

## Mission
You are the autonomous senior engineering team responsible for auditing, extending, validating, and **publishing** the provided **EVIDORIX / ClinOR v0.3.0 research prototype** as a professional open-source GitHub project. Work in the real repository, edit real files, run actual tests, and ship deliverables. Do not substitute a planning document or mock screens for working code. The existing repository is the starting point, not a specification to trust blindly.

**Authorized GitHub destination:** `asas2000034-spec/ClinOR-Engine` (public repository). Create it if it does not exist. Publish only to the authenticated account whose login is exactly `asas2000034-spec`. The user explicitly requests public GitHub publication of this project. Never force push, overwrite unrelated history, or publish secrets or patient data. If account authorization/permissions are absent, complete all local work and return the exact blocker and safe commands needed to finish publication; do not claim it was published.

## Mandatory product-wide language policy — ENGLISH ONLY (en-US)
All application, marketing, research and developer-facing content must use professional US English, left-to-right. Apply this to UI navigation, forms, tooltips, errors, dashboards, charts, clinical analysis, AI responses, optimization outputs, PDF/report exports, API documentation, README, GitHub templates, release notes, social previews, and editable Slidev brand collateral.
- No Arabic, bilingual interface, locale toggle, non-English onboarding, or Arabic summary in the delivered repository.
- Prompts and structured-output contracts must request English responses; verify generated sections are English while preserving source-title and quoted original-language evidence when essential for traceability. Do not change clinical concepts or source titles to satisfy a language checker.
- A retrieval engine may search publications in any language; distinguish original-language excerpts from synthesized English clinical summaries.
- Add automated checks for unintended untranslated UI/static strings (do not ban non-ASCII scientific symbols or citations).
- Use the editorial v2 brand assets; all brand slide copy and product screenshots must be English.
- Completion requires a real UI verification across primary routes, and no untranslated product-facing text.

## Product vision
Build **EVIDORIX — AI-Powered, Guideline-Grounded Clinical Evidence Research & Operations Research Platform**, a **condition-agnostic** modular platform. A user may ask about *any* condition, specialty, diagnosis, treatment pathway, or clinical decision question. A local or cloud LLM helps formulate searches, find and critically structure the evidence, and explain the results. Deterministic, auditable software validates source metadata, guideline version, provenance, evidence status, and expert-authored constraints. The operations-research layer selects methods suited to the mathematical decision problem and compares reviewed treatment alternatives. The output provides traceable options, uncertainty, and rationale for professional review, **not autonomous prescribing**.

Do not hard-code the entire platform around diabetes, nephrology, or any single condition. A few synthetic example domains may be used for tests; examples do not imply validated clinical coverage. Do not claim guidelines are verified just because they were retrieved; do not infer treatment efficacy, eligibility, dosage, contraindications, or interaction safety from an LLM alone.


## Canonical branding and migration — required, not optional

**This handoff supersedes all previous EVIDORIX turquoise/purple/glow branding.** The source snapshot includes a v1 web theme and older `brand/` assets solely because they are part of the currently working app. They are *not* the desired visual identity. The new and sole authority is `design/brand-v2/`:

- `design/brand-v2/brand/tokens.json` — canonical tokens: ink `#17191A`, vermilion `#C83C2D`, paper `#F6F3EC`, white `#FFFEFB`, slate `#6B7278`, hairline `#DED9D0`.
- `design/brand-v2/docs/BRAND_GUIDELINES.md` — usage and restrictions.
- `design/brand-v2/docs/CODEX_INTEGRATION.md` and `docs/CODEX_REBRAND_PROMPT.md` — integration steps.
- `design/brand-v2/public/assets/*.svg` — *primary editable vector wordmark/mark files*, no substitute logo generation.
- `design/brand-v2/social/` — approved GitHub/LinkedIn editorial preview exports (SVG + PNG).
- `design/brand-v2/slides.md`, `style.css`, `package.json` — 23-slide editable Slidev brand identity source.

Brand design language: **Swiss Editorial × Scientific Modernism**; warm paper, near-black typography, restrained vermilion decision cut and precise editorial grid. NO gradients, neon teal, purple-blue SaaS glows, generic brains/neural-network icons, medical crosses as logo, stock-like technology patterns, or unverified compliance badges. Vermilion is a brand accent and must never function as a clinical safety/status indicator.

Replace old v1 branding throughout application (HTML/CSS/JS), favicon, OpenGraph/social assets, README hero, screenshots, and GitHub metadata. Keep original `clinor` Python package, API endpoints and `CLINOR_*` env vars for backward compatibility until a measured, tested migration exists. Do not introduce external hosted fonts as a hard requirement; use licensed font stacks and local fallbacks, NEVER bundle font binaries. Test light and dark interface surfaces for contrast and focus; audit 390px mobile and >=1280px desktop. Keep Slidev sources editable and visually consistent with deployed site.

During this redesign, make sure existing research and OR functions remain accessible; no static mock-only UI, and no hidden feature regressions. Browser screenshots must be generated from actually running app to support the case study. When finished remove outdated brand assets rather than publishing two competing logos.

Before public release: prominently disclose that the **EVIDORIX name/mark have not been cleared by trademark counsel** and do not present the identity as legally protected/registered.

## Priority order

(1) Confirm baseline and repair breaking/security issues, (2) implement v2 brand faithfully, (3) strengthen local-first LLM and evidence provenance, (4) validate and extend OR method routing/clinical rule workflow, (5) run release gate and publish safely. Deliver a high-quality functional slice rather than claiming every medical specialty is clinically validated.

## Required execution procedure (complete, do not stop after planning)

### Phase 0 — inspect and audit the real codebase
1. Read `README.md`, `pyproject.toml`, `.env.example`, `SECURITY.md`, `docs/`, `clinor/`, `examples/`, tests and CI. Run `pytest -q`, `ruff check .`, Python compile, dependency inspection, and basic API smoke tests; report exact baseline successes/failures without inventing metrics.
2. Map existing endpoints, algorithms, provider gateways, data flows, licensing, and trust boundaries. Flag mathematical correctness weaknesses, use of heuristic scores, weak citation fidelity, untrusted tool output/prompt injection, cloud-consent bugs, ePHI leakage, dependency/network risks, input schema weaknesses, and web UI behavior. Validate claims from older README rather than repeating them.
3. Create a concise prioritized audit in `docs/AUDIT.md` with observed evidence and a repair plan, and implement high-priority repairs before feature expansion.

### Phase 1 — software architecture and local-first LLM integration
4. Refactor only where justified into testable interfaces, preferably `providers`, `retrieval`, `evidence`, `guidelines`, `clinical_rules`, `optimization`, `orchestrator`, `api`, `ui`. Preserve backward-compatible endpoints where practical; document breaking changes otherwise.
5. Implement provider abstraction with **Ollama native API**, **LM Studio / llama.cpp / vLLM OpenAI-compatible local API**, and **cloud OpenAI-compatible API**. Model names, base URLs and timeouts are configurable through environment variables. Prefer local inference by default. Health checks must distinguish configured vs connected vs inference-tested. Local-only mode should never send a prompt to remote LLM endpoints. Cloud use requires separate explicit user consent for each request. Do not commit any keys.
6. LLM duties: intent extraction; multi-query planning; source-aware evidence extraction; structured reasoning proposals; natural-language explanation. Use strict typed JSON schemas, retries with caps, validation, timeouts, and graceful degradation when model output is malformed. Record model/provider/version and prompt metadata (not private prompt contents) for reproducibility. Treat retrieved pages and model completions as untrusted input, not instructions.
7. Make model support realistic for 16GB-RAM computers (CPU and entry GPU); offer lightweight quantized-model configuration, optional larger models, optional cloud backend, and explicit resource expectations. Do not make a specific commercial provider mandatory.

### Phase 2 — real guideline/evidence retrieval (cross-specialty)
8. Support evidence search from Europe PMC (existing), and **well-documented, legally permitted** source adapters for guideline discovery. Evaluate official guideline and standards publisher sources as applicable (e.g. NICE, WHO, GINA, GOLD, ESC, ADA, KDIGO, IDSA, AHA/ACC, specialty societies). Do not assume any official publisher provides a free public API or permits scraping/republication. Use real APIs and stable search links where licensed; store only metadata, short permitted extracts, links, and approved annotations. Do not secretly scrape prohibited sites.
9. Return evidence objects with at least: `source_id`, title, organization, canonical URL, DOI/PMID when available, publication date, last-reviewed date if known, jurisdiction, publication type, guideline version when known, retrieval timestamp, quotation/snippet with provenance, and verification status. Distinguish *discovered*, *reviewed*, *approved rule*, *outdated*, *conflicting*, and *unavailable*. Never fabricate citations, URLs, access dates, or numeric effect sizes.
10. Establish evidence hierarchy, contradictory-guideline handling, explicit guideline regional scope, edition/version change detection when supported, provenance IDs, missing-evidence and abstention behavior. Assess RAG retrieval quality through labelled synthetic/non-sensitive evaluation examples; cite source identifiers that resolve to retrieved items.

### Phase 3 — clinical constraints and expert review
11. Design a **general, disease-independent schema** for condition context, patient features, interventions, outcomes, evidence, contraindication/prerequisite rules, decision constraints, and preferences. Consider FHIR-oriented exchange semantics but do not promise full FHIR interoperability until implemented and tested.
12. An LLM may *propose* candidate constraints in a DRAFT workspace with source spans. It MUST NOT auto-promote them to clinical rules. A separate **reviewed, versioned approval pathway** with tests, reviewer identity, provenance, effective dates, change logs and explicit states is required before clinical rule use. Unknown critical information triggers data-needed/abstain instead of confident ranking. Never convert a therapeutic risk or contraindication into a low weighted penalty.
13. Keep clinical hard constraints distinct from adjustable preferences; separate safety checks from utility optimization. Display alternative options, evidence strength/uncertainty and reasons for exclusion. Never claim patient-specific clinical efficacy is mathematically proven.

### Phase 4 — multi-method operations research, not just MILP
14. Audit and improve the existing SciPy MILP/HiGHS, optional CP-SAT, MCDA (TOPSIS, weighted sum), Pareto, stochastic and robust optimization, Monte Carlo, Markov cohort, dynamic programming and queueing methods. Mathematically cross-check tiny problems with brute-force or analytic reference solutions; assert infeasibility handling, numerical stability, determinism, unit constraints, probability sums, dominance rules, and reproducible random seeds. Do not count queueing theory as a treatment-ranking algorithm.
15. Add/strengthen a transparent OR method selector based on problem structure, objectives, horizon, dependencies, uncertainty and data availability. An LLM may recommend a method, but a deterministic validator confirms suitability and required parameters. If inputs are not sufficient, return `not_computable` with missing assumptions. Make objective normalization and preference weights explicit, provide sensitivity analyses and Pareto frontiers where appropriate; never silently invent clinical utilities or transition probabilities.
16. Benchmark at least representative small and medium **synthetic** problems. Log status, solver version, time limit, optimality/feasibility, objective, bound/gap where available; distinguish proven optimum from heuristic or time-limited solutions. Do not fabricate speedups or hospital cost savings.

### Phase 5 — usable application and engineering quality
17. Implement the *v2 editorial brand*, and create a polished, responsive, accessible UI for: question/case input with clear de-identification guidance; local/cloud provider configuration and connectivity; research plan; evidence explorer with verifiable source links; review/approval status; OR method selection; explicit editable synthetic/reviewer-provided parameters; comparison/uncertainty results; audit trail. Clearly mark *research prototype* and distinguish proposed from approved clinical content. No mock recommendations described as real.
18. Provide typed FastAPI API with OpenAPI docs, validated schemas, resilient network clients, bounded concurrency/timeouts, rate limiting suitable for a prototype, clear error responses, audit identifiers and privacy-preserving logs. Use feature flags for incomplete integrations. Add Docker and clear local startup paths.
19. Add meaningful unit, property-based where useful, integration and contract tests; deterministic mocks for external services; optional live smoke tests behind opt-in network flags. Add CI (pytest, lint, type checking if practical, dependency/security checks, secret scan), coverage report, reproducible example datasets, threat model, CONTRIBUTING, LICENSE, CODE_OF_CONDUCT, SECURITY, issue/PR templates, CHANGELOG and clear architectural docs. Avoid bloated dependency trees and prohibit bundled paid/proprietary guideline text.
20. Add `docs/VALIDATION.md` specifying exact tested coverage and what is not validated, and `docs/PORTFOLIO_CASE_STUDY.md` with screenshots or reproducible example outputs, scientifically honest before/after comparisons, architecture and tradeoffs. Include an English-only README, portfolio materials, release notes and developer documentation. Do not add a bilingual or Arabic product interface. Keep user-visible documents free of internal tool chatter.

### Phase 6 — release quality gate
21. Run all checks in the actual environment and fix errors. At minimum run: `python -m pytest -q`, `ruff check .`, `python -m compileall -q clinor`, basic app startup/health verification, example CLI/API runs, and `git diff --check`. Verify sample outputs, URLs and claims. Keep a summary of executed commands, results and anything not verified. Update `docs/RELEASE_VERIFICATION.md` with observed output, not expectations.
22. Scan tracked files for tokens, `.env`, credentials, access keys, local patient content, developer caches, virtual environments, `__pycache__`, log files, and generated binary output. Do not publish any personal health information or private data. Only project code and safe, synthetic examples may be committed. README must clearly state no clinical validation and no autonomous prescribing.
23. Never fabricate test counts, publication URLs, clinical endorsements, product maturity, compliance status, scientific novelty, or code execution results.

### Phase 7 — create and publish to MY GitHub account
24. Verify `gh auth status` and `gh api user --jq .login` (or available equivalent authenticated GitHub interface). **Proceed only if the GitHub login is `asas2000034-spec`.** If another account is authenticated, stop only the publication step, explain how to switch accounts; keep all completed code.
25. If `asas2000034-spec/ClinOR-Engine` does not exist: initialize Git (`main`), commit the clean source tree and create **PUBLIC** repository `ClinOR-Engine` with description `Open-source local-first AI clinical evidence research and operations research platform`. Prefer `gh repo create asas2000034-spec/ClinOR-Engine --public --source=. --remote=origin --push` after auth. NOTE: repository slug remains ClinOR-Engine from the previous explicit instruction; product branding displayed on GitHub/website is EVIDORIX. Do NOT rename the repository without a new user decision. The exact official procedure may be adapted to the installed CLI. If the repo already exists: fetch and inspect; preserve existing history; commit to a feature branch and open a PR for review if necessary. **No `--force`, no destructive overwrite, no other repository**.
26. Verify remote URL, commit SHA, visible source files and GitHub Actions status (if checks are still pending, say pending). Create an initial post-audit version tag/release only if the code passes the release gate, clearly marking it as a research prototype. Prefer an appropriately incremented version and include truthful release notes.
27. Report the exact **live GitHub repository URL**, default branch, commit SHA, status of CI, runnable local instructions and remaining limitations. If publication is blocked, do not invent a link or say successful: report the reason and minimal user authentication step.

## Definition of Done
- A non-disease-specific, documented, executable, extensible research platform, with AI retrieval and separate, mathematically verifiable OR engines.
- Local LLM inference path usable without cloud API keys; cloud optional and explicitly gated.
- Verified citations and provenance; no unreviewed automatic treatment rules.
- Existing and added tests really executed; math and security assumptions documented.
- Polished public GitHub repository under `asas2000034-spec` **if authentication/permissions allow**; otherwise code complete and exact publication blocker disclosed.

**Execution style:** prioritize shipping a reliable vertical slice over superficially implementing dozens of functions. Implement, test, repair and commit in logical increments. You are authorized to publish this project publicly to the named account; do not ask for approval again unless GitHub authentication or the environment itself requires the user's action. Do not stop after providing a roadmap. Work to completion using tools available in the Codex environment.


## Hard acceptance criteria for THIS handoff
- Actual working app rebranded with v2 identity, not just a new PDF or screenshot.
- `design/brand-v2/` stays editable, including 23 Slidev slides and original SVG assets.
- Research engine remains cross-specialty and LLM provider-agnostic (local-first; cloud optional and consented).
- OR engine inventory remains mathematically honest; no unsupported all-disease treatment ranking.
- No real patient data, API keys, `.env` or proprietary guideline bodies committed.
- Tests and lint reported with actual output and failures clearly separated.
- GitHub publication targets *only* `asas2000034-spec/ClinOR-Engine` (public) if authenticated, with commit SHA and reachable URL.
- Product README and portfolio materials use EVIDORIX; internal `clinor` namespace can remain for compatibility.
