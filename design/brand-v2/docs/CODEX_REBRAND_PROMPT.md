# Codex implementation instruction — EVIDORIX editorial rebrand

Use this folder as the canonical design system for EVIDORIX. Work in the ClinOR/EVIDORIX application repository, not in the brand slides directory.

1. Read `docs/BRAND_GUIDELINES.md`, `brand/tokens.json` and review the `slides.md` visual direction.
2. Audit all current UI assets, color tokens, logos, Favicons, social previews and README graphics. Identify obsolete turquoise/purple/glow styling.
3. Implement the new editorial identity with the outlined SVG marks, one vermilion accent, paper/ink palette, legible typography, and a 12-column typographic grid.
4. Keep backend functionality, Python package names, APIs, and clinical evidence/optimization logic unchanged unless a modification is required and tested.
5. Create reusable UI tokens/components, update accessible states (do not indicate medical safety using brand red), and validate responsive layouts.
6. Replace all old screenshots and previews only after rendering current UI with browser snapshots.
7. Run all existing tests; perform new snapshot, a11y and contrast testing. Report failures rather than pretending they passed.
8. Open a reviewable pull request instead of force pushing; avoid changing repository visibility or publishing any credentials.

Deliver: changed file inventory, screens before/after, test results and a link to the PR when possible.
