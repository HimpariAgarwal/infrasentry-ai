from dataclasses import dataclass
from typing import Callable, Any

from sla_scheduler_policy_engine import run_with_retry_policy


@dataclass(frozen=True)
class RetryProfile:
    name: str
    max_attempts: int
    initial_delay: float
    backoff_factor: float

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Profile name cannot be empty")

        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool):
            raise TypeError("max_attempts must be an integer")

        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        if self.initial_delay < 0:
            raise ValueError("initial_delay cannot be negative")

        if self.backoff_factor < 1:
            raise ValueError("backoff_factor must be at least 1")


PROFILES = {
    "fast": RetryProfile(
        name="fast",
        max_attempts=2,
        initial_delay=0.5,
        backoff_factor=2,
    ),
    "standard": RetryProfile(
        name="standard",
        max_attempts=3,
        initial_delay=1,
        backoff_factor=2,
    ),
    "conservative": RetryProfile(
        name="conservative",
        max_attempts=3,
        initial_delay=3,
        backoff_factor=3,
    ),
}


def get_retry_profile(name: str) -> RetryProfile:
    if not isinstance(name, str):
        raise TypeError("Profile name must be a string")

    normalized = name.strip().lower()

    try:
        return PROFILES[normalized]
    except KeyError:
        raise ValueError(f"Unknown retry profile: {name}") from None


def execute_with_profile(
    func: Callable[[], Any],
    profile_name: str = "standard",
    sleep_func: Callable[[float], None] | None = None,
) -> dict:
    profile = get_retry_profile(profile_name)

    kwargs = {
        "max_attempts": profile.max_attempts,
        "initial_delay": profile.initial_delay,
        "backoff_factor": profile.backoff_factor,
    }

    if sleep_func is not None:
        kwargs["sleep_func"] = sleep_func

    return run_with_retry_policy(func, **kwargs)
