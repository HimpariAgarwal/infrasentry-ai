from fastapi import APIRouter
from backend.incident_analytics import generate_incident_analytics

router = APIRouter(prefix="/api/v1/incidents", tags=["Incident Analytics"])


@router.get("/analytics")
def incident_analytics():
    return generate_incident_analytics()
