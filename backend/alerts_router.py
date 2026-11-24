from fastapi import APIRouter, HTTPException
from backend.security_alerts import (
    generate_security_alerts,
    get_security_alerts,
    resolve_security_alert,
)

router = APIRouter(prefix="/api/v1/security", tags=["Security Alerts"])


@router.post("/alerts/generate")
def generate_alerts():
    return generate_security_alerts()


@router.get("/alerts")
def list_alerts():
    return {"alerts": get_security_alerts()}


@router.patch("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    if not resolve_security_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved", "alert_id": alert_id}
