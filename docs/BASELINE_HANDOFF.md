# Verified handoff baseline

Snapshot: EVIDORIX / ClinOR v0.3.0 (v1 interface included as the starting code state).
Brand target: EVIDORIX Editorial Identity v2 under `design/brand-v2/` — **NOT yet merged into the functional UI**.

Verification observed while assembling package:
- `cd /mnt/data/EVIDORIX-ClinOR-Branded-Handoff && python -m pytest -q` => **50 passed in 0.94s**.
- `python -m compileall -q` on original v0.3.0 module => exit success.
- `ruff` executable absent in preparation runtime => not run.
- Slidev runtime (npm CLI), real Ollama inference, external research provider calls, and GitHub remote publication not exercised.

Codex should run its own checks and update results. No clinical validation is implied.
