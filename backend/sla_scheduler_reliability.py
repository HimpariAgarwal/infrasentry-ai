import threading
import time
from functools import wraps

_execution_lock = threading.Lock()


def prevent_overlapping_runs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        acquired = _execution_lock.acquire(blocking=False)

        if not acquired:
            return {
                "status": "skipped",
                "reason": "Previous scheduler execution is still running",
            }

        started = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            duration = round(time.perf_counter() - started, 4)

            return {
                "status": "success",
                "duration_seconds": duration,
                "result": result,
            }

        except Exception as exc:
            duration = round(time.perf_counter() - started, 4)

            return {
                "status": "failed",
                "duration_seconds": duration,
                "error": str(exc),
            }

        finally:
            _execution_lock.release()

    return wrapper
