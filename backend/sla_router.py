from fastapi import APIRouter
from backend.sla_monitor import generate_sla_report

router = APIRouter(prefix="/api/v1/sla", tags=["SLA Monitoring"])

@router.get("/report")
def get_sla_report():
    return generate_sla_report()
