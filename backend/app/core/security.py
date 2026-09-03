from __future__ import annotations

import hmac
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings

_requests: dict[tuple[str, str], deque[int]] = defaultdict(deque)
EXPENSIVE_PATHS = {"/api/classify", "/api/classify/batch", "/api/ai/ask", "/api/learning/train", "/api/ingestion/run"}


def require_admin(request: Request, x_admin_key: str | None = Header(default=None)) -> None:
    settings = get_settings();host = request.client.host if request.client else ""
    if host in {"127.0.0.1", "::1", "testclient"} and settings.allow_unauthenticated_local_mutations:return
    if not settings.admin_api_key:raise HTTPException(503, "Administrative API access is not configured")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(401, "Invalid administrative API key", headers={"WWW-Authenticate": "X-Admin-Key"})


async def security_middleware(request: Request, call_next):
    settings = get_settings();client = request.client.host if request.client else "unknown"
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > settings.max_request_bytes:return JSONResponse({"detail":"Request body is too large"},status_code=413)
    minute = int(time.time() // 60);bucket = _requests[(client, request.url.path)]
    while bucket and bucket[0] < minute:bucket.popleft()
    limit = settings.expensive_rate_limit_per_minute if request.url.path in EXPENSIVE_PATHS else settings.api_rate_limit_per_minute
    if len(bucket) >= limit:return JSONResponse({"detail":"Rate limit exceeded"},status_code=429,headers={"Retry-After":"60"})
    bucket.append(minute);response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff";response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin";response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):response.headers["Cache-Control"] = "no-store"
    return response
