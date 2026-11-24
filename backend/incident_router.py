from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.incident_manager import (
    create_incident,
    list_incidents,
    update_incident,
)
from backend.security_alerts import get_security_alerts

router = APIRouter(prefix="/api/v1/incidents", tags=["Incident Management"])


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    note: Optional[str] = Field(default=None, max_length=1000)


@router.post("/from-alerts")
def create_from_alerts():
    created = []
    for alert in get_security_alerts():
        if alert.get("status") == "active":
            incident = create_incident(alert)
            if incident:
                created.append(incident)

    return {"created": len(created), "incidents": created}


@router.get("")
def get_incidents(status: str = "all"):
    allowed = {"all", "open", "investigating", "resolved"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    return {"incidents": list_incidents(status)}


@router.patch("/{incident_id}")
def patch_incident(incident_id: str, payload: IncidentUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if "status" in updates and updates["status"] not in {
        "open", "investigating", "resolved"
    }:
        raise HTTPException(status_code=400, detail="Invalid incident status")

    if "assigned_to" in updates and updates["assigned_to"] is not None:
        updates["assigned_to"] = updates["assigned_to"].strip()
        if not updates["assigned_to"]:
            raise HTTPException(status_code=400, detail="Assignee cannot be empty")

    incident = update_incident(incident_id, updates)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident
