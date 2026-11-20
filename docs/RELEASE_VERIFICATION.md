# Release verification

- Windows, CPython 3.12. Baseline pytest returned 50 passes. Revised suite returned 53 passes with OR-Tools installed. Coverage measured 84% during implementation.
- Ruff and compileall passed. The running FastAPI health route returned OK. Both desktop and mobile browser sessions completed MCDA and passed the horizontal overflow assertion.
- A live Europe PMC query returned PMID 42785634. This verifies adapter connectivity only.
- The local Ollama probe returned ConnectError. Cloud inference, live LM Studio and clinical performance remain unverified.
- pip-audit reported no known vulnerabilities among audited installed dependencies and skipped the editable project. The Slidev dependency audit initially reported eight findings. Patched transitive dependencies cleared the audit.
- Docker Desktop's engine pipe was unavailable. Container execution was not verified.
