import os
import jwt

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


PROTECTED_PREFIXES = (
    "/api/v1/detect",
    "/api/v1/history",
    "/api/v1/logs",
    "/api/v1/system-health",
)


class APIAccessControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        protected = any(
            path == prefix or path.startswith(prefix + "/")
            for prefix in PROTECTED_PREFIXES
        )

        if not protected:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1].strip()
        secret = os.getenv("JWT_SECRET_KEY", "")

        if not secret or len(secret) < 32:
            return JSONResponse(
                status_code=503,
                content={"detail": "JWT authentication is not configured."},
            )

        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
            )

            if not payload.get("sub"):
                raise jwt.InvalidTokenError("Missing subject")

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token expired."},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication token."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user = payload["sub"]
        return await call_next(request)
