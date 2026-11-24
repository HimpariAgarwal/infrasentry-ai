from fastapi import APIRouter, HTTPException

from sla_scheduler_retry_profiles import PROFILES, get_retry_profile

router = APIRouter(
    prefix="/api/v1/sla/retry-profiles",
    tags=["SLA Retry Profiles"],
)


def serialize_profile(profile):
    return {
        "name": profile.name,
        "max_attempts": profile.max_attempts,
        "initial_delay": profile.initial_delay,
        "backoff_factor": profile.backoff_factor,
    }


@router.get("")
def list_retry_profiles():
    return {
        "profiles": [
            serialize_profile(PROFILES[name])
            for name in sorted(PROFILES)
        ],
        "total": len(PROFILES),
    }


@router.get("/{profile_name}")
def read_retry_profile(profile_name: str):
    try:
        profile = get_retry_profile(profile_name)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Retry profile '{profile_name}' not found",
        )

    return {"profile": serialize_profile(profile)}
