# Apply EVIDORIX Editorial Identity to the ClinOR codebase

1. **Audit** existing logos, colors, theme tokens, favicons, README badges and screenshots.
2. **Do not rename internal Python package `clinor` automatically**; compatibility, entry points and tests must continue to function.
3. Copy outlined SVG assets to application static assets. Add light/reverse marks and compact icon.
4. Replace cyan/purple/dark-glow theme with colors defined in `brand/tokens.json`. Introduce editorial layout grid, typography hierarchy and accessible contrast checks.
5. Replace generic network graphics with traceable evidence→analysis→decision information patterns.
6. Use new GitHub/LinkedIn preview graphics only after reviewing exported sizing and reading order.
7. Run frontend snapshot tests, backend tests, accessibility checks and inspect both 1440px desktop and 390px mobile screens.
8. Do not make unsupported claims of clinical validation, autonomous prescription or guaranteed decision superiority.
9. Keep local/cloud LLM selection and all mathematical engines independent of visual branding.
10. Update project docs and disclose old brand name as a legacy internal implementation identifier where necessary.
