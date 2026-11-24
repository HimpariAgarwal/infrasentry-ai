from fastapi import APIRouter, HTTPException

from sla_scheduler_retry_profiles import get_retry_profile
from sla_scheduler_retry_preview import build_retry_preview

router = APIRouter(
    prefix="/api/v1/sla/retry-preview",
    tags=["SLA Retry Preview"],
)


@router.get("/{profile_name}")
def get_retry_profile_preview(profile_name: str):
    try:
        profile = get_retry_profile(profile_name)
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=404,
            detail=f"Retry profile '{profile_name}' not found",
        )

    return build_retry_preview(profile)
