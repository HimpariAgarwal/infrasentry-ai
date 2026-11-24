from fastapi import APIRouter, HTTPException, Query

from backend.sla_alerts import (
    generate_sla_alerts,
    get_sla_alerts,
    resolve_sla_alert,
)

router = APIRouter(prefix="/api/v1/sla", tags=["SLA Alerts"])

@router.get("/alerts")
def list_sla_alerts(status: str | None = Query(default=None)):
    return {
        "alerts": get_sla_alerts(status),
        "status": "success",
    }

@router.post("/alerts/generate")
def create_sla_alerts():
    return generate_sla_alerts()

@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    result = resolve_sla_alert(alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="SLA alert not found")
    return {"status": "success", "alert": result}
