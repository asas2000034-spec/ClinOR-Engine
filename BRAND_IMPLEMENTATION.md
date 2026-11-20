# EVIDORIX v2 — Brand implementation checklist for Codex

**Source of truth:** `design/brand-v2/`. The `brand/` folder at repository root belongs to the obsolete first visual identity and must be replaced/deleted after migration. Do not use its teal/purple logo, palette or social previews.

## Must preserve exactly
- `design/brand-v2/brand/tokens.json` color values; no gradient/glow overlays.
- Outlined vector wordmark from `design/brand-v2/public/assets/wordmark-ink.svg`, dark variant `wordmark-reversed.svg`, compact `mark-ink.svg`.
- Brand proposition: **From evidence to defensible decisions.**
- Clinical evidence → analysis → decision is an information-flow motif, not an assertion of clinical approval.
- SVG originals and 23 editable Slidev slides are versioned; fonts are referenced, not bundled.

## Implement in app
1. Replace v1 logo, favicon, navbar/sidebar, browser tab icon, OpenGraph hero, website metadata and stale badges.
2. Establish CSS tokens and reusable typographic/layout components.
3. Design light-first editorial dashboard with optional readable dark states; preserve form function and accessible statuses.
4. Refactor old v1 tightly compressed CSS into maintainable styles without changing unrelated business behavior.
5. Create proper layouts for literature search, guideline evidence cards, retrieved/discovered/reviewed states, solver workbench, AI provider status and audit trail.
6. Visually QA desktop 1440px and iPhone-like 390px; run smoke tests and check overflow, contrast and keyboard focus.
7. Generate honest screenshot(s) of actual running app, update README after implementation. Do not use brand mockups as app screenshots.
8. Recheck brand v2 Slidev with npm when available (not confirmed run during original creation).
9. Remove old v1 brand files/assets after verifying there are no broken references.

## Brand status and legal
Trademark clearance for EVIDORIX has **not** been completed; do not claim it is registered or exclusive. A launch-brand decision is not a patent or device clearance.

## Language
All delivered brand and product copy must be English (en-US), including Slidev, web UI, release assets and README. No Arabic or bilingual brand components.
