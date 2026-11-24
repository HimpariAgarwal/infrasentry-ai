from fastapi import APIRouter

from sla_scheduler_retry_comparison import compare_retry_profiles

router = APIRouter(
    prefix="/api/v1/sla/retry-comparison",
    tags=["SLA Retry Comparison"],
)


@router.get("/")
def get_retry_profile_comparison():
    return compare_retry_profiles()
