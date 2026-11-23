# API Access Controls — EVIDORIX

The repository originally exposed public research/optimization API routes for a **local-only research workbench**. This update adds an opt-in, fail-closed shared-secret barrier. It is a hardening increment, **not** a declaration of clinical or public-production readiness.

## Enable

Set environment variables in the runtime, not in Git:

```bash
export CLINOR_AUTH_REQUIRED=true
export CLINOR_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
uvicorn clinor.api:app --host 127.0.0.1 --port 8000
```

API calls then require:

```bash
curl -H "X-API-Key: $CLINOR_API_KEY" http://127.0.0.1:8000/api/or/algorithms
```

or an HTTP Authorization Bearer token.

- `/api/health` remains public for liveness checks.
- All other `/api/*` routes require a secret whenever `CLINOR_AUTH_REQUIRED` is enabled **or** `CLINOR_API_KEY` is present.
- A key shorter than 24 characters or a missing key with required auth returns HTTP 503, not an unauthenticated fallback.
- Headers include request ID, `Cache-Control: no-store` for APIs, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`.
- The web UI currently does not attach shared-secret headers to all API calls. When enabling authentication, use authenticated API clients or implement a browser/session gateway. Do **not** paste a shared key into public frontend source.
- The existing request limiter is **per process**, not a distributed abuse-prevention system.

## Remaining work for public multi-user deployments

Trusted reverse proxy with TLS, identity provider/OIDC, roles and permissions, audit persistence, request-size and concurrency quotas, data retention controls, secret rotation, security review, and consent-aware handling for external LLM calls. Medical governance and independent clinical validation remain separate release blockers.
