from fastapi import APIRouter
from backend.threat_detection import analyze_security_events

router = APIRouter(prefix="/api/v1/security", tags=["Threat Analytics"])


@router.get("/threat-analysis")
def threat_analysis():
    return analyze_security_events()
