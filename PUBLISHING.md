# EVIDORIX GitHub publication checklist

User-approved target: `asas2000034-spec/ClinOR-Engine` (**PUBLIC**). EVIDORIX is the product name, `ClinOR-Engine` the legacy repository slug unless the user explicitly changes it.

1. Run baseline tests, lint, code compile, app smoke tests and brand UI verification. Record exact results and remaining gaps.
2. Inspect `git status`, `.gitignore`, tracked binary files, `.env*`, file history, keys and PII. Use synthetic data only.
3. Inspect `gh auth status` and `gh api user --jq .login`. Proceed only when login is exactly `asas2000034-spec`.
4. Check whether target repo exists. If absent: `git init -b main`, stage clean files, commit, then `gh repo create asas2000034-spec/ClinOR-Engine --public --source=. --remote=origin --push`. If present: fetch and preserve history, use branch/PR. No force push.
5. Add concise description, README hero with actual v2 branding, topics, license and sensible demo/use warnings. Do not claim clinical validation.
6. Verify the URL from GitHub, remote, branch, SHA, CI run. If CI not completed, state pending.
7. Report exactly what published and what remains unimplemented; if auth is absent, stop only this publishing step.

Never create a repository in a different account, and do not claim remote publication based solely on a local git commit.
