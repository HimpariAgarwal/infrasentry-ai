import time
from typing import Any, Callable

from sla_scheduler_retry_policy import classify_retry_error, should_retry
from sla_scheduler_retry_metrics import record_retry_run


def run_with_retry_policy(
    func: Callable[[], Any],
    max_attempts: int = 3,
    initial_delay: float = 1,
    backoff_factor: float = 2,
    sleep_func: Callable[[float], None] = time.sleep,
) -> dict:
    """
    Run an operation using the conservative retry policy.

    Retryable errors: connection and timeout errors.
    Permanent errors: stop immediately.
    Metrics are recorded once per execution.
    """
    if not callable(func):
        raise TypeError("func must be callable")

    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
        raise TypeError("max_attempts must be an integer")

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    if initial_delay < 0:
        raise ValueError("initial_delay cannot be negative")

    if backoff_factor < 1:
        raise ValueError("backoff_factor must be at least 1")

    started = time.monotonic()
    attempts = 0
    last_error = None
    status = "failed"
    result = None

    try:
        while attempts < max_attempts:
            attempts += 1

            try:
                result = func()
                status = "success"
                return {
                    "success": True,
                    "attempts": attempts,
                    "result": result,
                    "error": None,
                }

            except Exception as exc:
                last_error = exc

                if not should_retry(exc, attempts, max_attempts):
                    break

                delay = initial_delay * (backoff_factor ** (attempts - 1))
                sleep_func(delay)

        return {
            "success": False,
            "attempts": attempts,
            "result": None,
            "error": str(last_error) if last_error else "Execution failed",
        }

    finally:
        duration = time.monotonic() - started
        try:
            record_retry_run(
                status=status,
                attempts=max(1, attempts),
                duration_seconds=duration,
                error=str(last_error) if last_error else None,
            )
        except Exception:
            # Metrics failure must not hide the operation's result.
            pass
