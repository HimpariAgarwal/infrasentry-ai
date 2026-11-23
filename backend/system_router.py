from fastapi import APIRouter, HTTPException

from system_monitor import get_system_health

router = APIRouter(prefix="/api/v1", tags=["System Monitoring"])


@router.get("/system-health")
def system_health():
    try:
        result = get_system_health()

        if not result["database"]["connected"]:
            result["status"] = "degraded"

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"System monitoring failed: {str(error)[:200]}",
        )
