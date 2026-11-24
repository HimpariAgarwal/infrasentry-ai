from fastapi import APIRouter, HTTPException

from sla_scheduler_retry_metrics import get_retry_metrics

router = APIRouter(tags=["SLA Retry Metrics"])


@router.get("/api/v1/sla/retry-metrics")
def retry_metrics():
    try:
        return get_retry_metrics()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve SLA retry metrics"
        ) from exc
