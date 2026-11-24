from fastapi import APIRouter

from backend.sla_scheduler import get_sla_scheduler_status

router = APIRouter(prefix="/api/v1/sla", tags=["SLA Automation"])


@router.get("/scheduler-status")
def scheduler_status():
    return get_sla_scheduler_status()
