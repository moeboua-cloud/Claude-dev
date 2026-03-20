"""Rate limiting middleware using in-memory sliding window."""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Sliding window: {client_key: [(timestamp, ...),]}
_request_log: dict[str, list[float]] = defaultdict(list)

# Rate limit config
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 120  # max requests per window
RATE_LIMIT_BURST = 30  # max burst in 5 seconds


def _get_client_key(request: Request) -> str:
    """Get client identifier from request."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _cleanup_old_entries(entries: list[float], now: float) -> list[float]:
    """Remove entries older than the window."""
    cutoff = now - RATE_LIMIT_WINDOW
    return [t for t in entries if t > cutoff]


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)

        client_key = _get_client_key(request)
        now = time.monotonic()

        # Clean old entries
        _request_log[client_key] = _cleanup_old_entries(_request_log[client_key], now)

        # Check rate limit
        if len(_request_log[client_key]) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)},
            )

        # Check burst limit (last 5 seconds)
        burst_cutoff = now - 5
        recent = [t for t in _request_log[client_key] if t > burst_cutoff]
        if len(recent) >= RATE_LIMIT_BURST:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": "5"},
            )

        _request_log[client_key].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, RATE_LIMIT_MAX_REQUESTS - len(_request_log[client_key]))
        )
        return response
