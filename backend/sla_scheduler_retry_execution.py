import time
from typing import Any, Callable

from sla_scheduler_retry import run_with_retries
from sla_scheduler_retry_metrics import record_retry_run


MAX_ATTEMPTS = 3
INITIAL_DELAY = 1
BACKOFF_FACTOR = 2


def execute_sla_generation_with_retry(
    generator: Callable[[], Any],
) -> Any:
    """Execute SLA generation with bounded retries and record retry metrics."""
    started = time.monotonic()
    result = None
    error_message = None
    status = "failed"
    attempts = MAX_ATTEMPTS

    try:
        result = run_with_retries(
            generator,
            max_attempts=MAX_ATTEMPTS,
            initial_delay=INITIAL_DELAY,
            backoff_factor=BACKOFF_FACTOR,
        )

        if not isinstance(result, dict):
            raise TypeError("Retry helper must return a dictionary.")

        attempts = int(result.get("attempts", MAX_ATTEMPTS))
        success_value = result.get("success")

        if success_value is None:
            success_value = result.get("status") in (
                "success",
                "succeeded",
                "ok",
            )

        if success_value:
            status = "success"
            return result.get("result")

        error_message = str(
            result.get("error") or result.get("message") or "SLA generation failed"
        )
        raise RuntimeError(error_message)

    except Exception as exc:
        error_message = str(exc)
        raise

    finally:
        duration = time.monotonic() - started
        record_retry_run(
            status=status,
            attempts=max(1, attempts),
            duration_seconds=duration,
            error=error_message,
        )
