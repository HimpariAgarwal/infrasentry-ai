import time


def run_with_retries(
    func,
    max_attempts=3,
    initial_delay=1,
    backoff_factor=2,
    sleep_func=time.sleep,
):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    if initial_delay < 0:
        raise ValueError("initial_delay cannot be negative")

    if backoff_factor < 1:
        raise ValueError("backoff_factor must be at least 1")

    attempts = 0
    delay = initial_delay
    last_error = None

    while attempts < max_attempts:
        attempts += 1

        try:
            result = func()
            return {
                "status": "success",
                "attempts": attempts,
                "result": result,
                "error": None,
            }

        except Exception as exc:
            last_error = str(exc)

            if attempts < max_attempts:
                sleep_func(delay)
                delay *= backoff_factor

    return {
        "status": "failed",
        "attempts": attempts,
        "result": None,
        "error": last_error,
    }
