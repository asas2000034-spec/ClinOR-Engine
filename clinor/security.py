"""Optional shared-secret API protection for deployments behind a trusted gateway.

This is an initial authorization boundary, not a multi-user identity system.
"""
from __future__ import annotations

import hmac
import os

from fastapi import Request
from fastapi.responses import JSONResponse


def _enabled() -> bool:
    requested = os.getenv("CLINOR_AUTH_REQUIRED", "").strip().lower()
    return requested in {"1", "true", "yes", "on"} or bool(os.getenv("CLINOR_API_KEY"))


def api_auth_error(request: Request, request_id: str) -> JSONResponse | None:
    """Fail closed if enabled but configuration is invalid.

    Local development remains unchanged when both env vars are absent.
    """
    if not request.url.path.startswith("/api/"):
        return None
    if request.url.path == "/api/health":
        return None
    if not _enabled():
        return None

    configured = os.getenv("CLINOR_API_KEY", "")
    if len(configured) < 24:
        return JSONResponse(
            status_code=503,
            content={"detail": "API authentication is not correctly configured"},
            headers={"X-Request-ID": request_id, "Cache-Control": "no-store"},
        )
    supplied = request.headers.get("X-API-Key", "")
    bearer = request.headers.get("Authorization", "")
    if not supplied and bearer.startswith("Bearer "):
        supplied = bearer[len("Bearer "):]
    if not hmac.compare_digest(supplied, configured):
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized"},
            headers={
                "X-Request-ID": request_id,
                "Cache-Control": "no-store",
                "WWW-Authenticate": "Bearer",
            },
        )
    return None


def harden_headers(response, request: Request) -> None:
    """Apply inexpensive defense-in-depth headers consistently."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
