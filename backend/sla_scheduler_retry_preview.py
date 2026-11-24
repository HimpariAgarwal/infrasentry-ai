def build_retry_preview(profile):
    """Build a read-only retry schedule from a retry profile."""
    attempts = profile.max_attempts
    initial_delay = profile.initial_delay
    backoff_factor = profile.backoff_factor

    schedule = []
    cumulative_wait = 0.0

    for attempt in range(1, attempts + 1):
        if attempt == 1:
            delay = 0.0
        else:
            delay = initial_delay * (backoff_factor ** (attempt - 2))

        cumulative_wait += delay

        schedule.append({
            "attempt": attempt,
            "delay_before_attempt_seconds": round(delay, 6),
            "cumulative_wait_seconds": round(cumulative_wait, 6),
        })

    return {
        "profile": profile.name,
        "max_attempts": attempts,
        "initial_delay": initial_delay,
        "backoff_factor": backoff_factor,
        "total_wait_seconds": round(cumulative_wait, 6),
        "schedule": schedule,
    }
