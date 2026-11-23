from collections import defaultdict, deque
from time import monotonic

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 120,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.request_history = defaultdict(deque)

    async def dispatch(self, request, call_next):
        # Apply limits only to API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        now = monotonic()
        requests = self.request_history[client_ip]

        # Remove expired requests
        while requests and now - requests[0] >= self.window_seconds:
            requests.popleft()

        # Reject excessive requests
        if len(requests) >= self.requests_per_minute:
            retry_after = max(
                1,
                int(self.window_seconds - (now - requests[0]))
            )

            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": "Too many API requests. Please try again later.",
                    "limit": self.requests_per_minute,
                    "window_seconds": self.window_seconds,
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        requests.append(now)
        response = await call_next(request)

        remaining = max(
            0,
            self.requests_per_minute - len(requests)
        )

        response.headers["X-RateLimit-Limit"] = str(
            self.requests_per_minute
        )
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
