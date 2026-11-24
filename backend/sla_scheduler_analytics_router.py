from fastapi import APIRouter

from backend.sla_scheduler_metrics import get_scheduler_metrics

router = APIRouter(
    prefix="/api/v1/sla",
    tags=["SLA Scheduler Analytics"],
)


@router.get("/scheduler-analytics")
def scheduler_analytics():
    return get_scheduler_metrics()
