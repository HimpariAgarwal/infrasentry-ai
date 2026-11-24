from sla_scheduler_retry_profiles import get_retry_profile
from sla_scheduler_retry_preview import build_retry_preview


def compare_retry_profiles():
    profile_names = ["fast", "standard", "conservative"]
    comparisons = []

    for name in profile_names:
        profile = get_retry_profile(name)
        preview = build_retry_preview(profile)

        comparisons.append({
            "profile": preview["profile"],
            "max_attempts": preview["max_attempts"],
            "initial_delay": preview["initial_delay"],
            "backoff_factor": preview["backoff_factor"],
            "total_wait_seconds": preview["total_wait_seconds"],
        })

    return {
        "profiles_compared": len(comparisons),
        "profiles": comparisons,
    }
