from typing import Literal

RetryClassification = Literal["retryable", "permanent"]


def classify_retry_error(error: Exception) -> RetryClassification:
    """
    Classify errors conservatively.

    Only temporary connection and timeout errors are retryable.
    Permission errors are permanent even though they inherit OSError.
    """
    if isinstance(error, PermissionError):
        return "permanent"

    if isinstance(error, (TimeoutError, ConnectionError)):
        return "retryable"

    return "permanent"


def should_retry(
    error: Exception,
    attempt_number: int,
    max_attempts: int,
) -> bool:
    """Return whether another retry attempt is permitted."""
    if not isinstance(attempt_number, int) or isinstance(attempt_number, bool):
        raise TypeError("attempt_number must be an integer")

    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
        raise TypeError("max_attempts must be an integer")

    if attempt_number < 1:
        raise ValueError("attempt_number must be at least 1")

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    if attempt_number >= max_attempts:
        return False

    return classify_retry_error(error) == "retryable"
