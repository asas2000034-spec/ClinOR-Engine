# EVIDORIX — Editorial Identity System

Editable, vector-first visual identity for an open-source clinical evidence and operations research platform.

## Contents
- `slides.md` — 23-slide editable Slidev brand manual
- `style.css` — scalable, responsive typography/layout rules for the presentation
- `public/assets/` — vector-path wordmarks and monograms (no proprietary font files)
- `social/` — editable SVG and share-ready PNG assets for GitHub & LinkedIn
- `brand/tokens.json` — design tokens for app developers
- `docs/BRAND_GUIDELINES.md` — brand system and usage rules
- `docs/CODEX_INTEGRATION.md` — steps for incorporating this identity in the application
- English-only editable Slidev source is authoritative; generate previews via Slidev after installing dependencies

## Run with Slidev

```bash
npm install
npm run dev
```

Export: `npm run export` (uses Slidev and Chromium). No font files are bundled.

## Important

The `slides.md` source is authoritative. Generate a fresh PDF or image preview from the source to avoid stale-language exports. This brand identity is a design proposal, not a verified registered trademark. The project provides clinical research and decision-analysis tooling, not autonomous medical prescribing.
