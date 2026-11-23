import logging
import time
from pathlib import Path

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("infrasentry.api")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(LOG_DIR / "api.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    ))
    logger.addHandler(handler)


class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration = (time.perf_counter() - start_time) * 1000

            logger.info(
                "%s %s | status=%s | duration=%.2fms",
                method,
                path,
                response.status_code,
                duration,
            )
            response.headers["X-Process-Time-Ms"] = f"{duration:.2f}"
            return response

        except Exception:
            duration = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "%s %s | FAILED | duration=%.2fms",
                method,
                path,
                duration,
            )
            raise
