from fastapi import APIRouter, Depends, HTTPException

from system_monitor import get_system_health
from auth_router import get_current_user
from system_diagnostics import collect_system_diagnostics

router = APIRouter(prefix="/api/v1", tags=["System Monitoring"])


@router.get("/system-health")
def system_health():
    try:
        result = get_system_health()

        if not result["database"]["connected"]:
            result["status"] = "degraded"

        return result

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="System monitoring failed.",
        )


@router.get("/system-diagnostics")
def system_diagnostics(current_user: dict = Depends(get_current_user)):
    """
    Protected system diagnostics endpoint.
    Requires a valid JWT bearer token.
    """

    try:
        return collect_system_diagnostics()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="System diagnostics unavailable.",
        )
