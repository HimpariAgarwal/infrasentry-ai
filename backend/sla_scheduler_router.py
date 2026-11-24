from fastapi import APIRouter, HTTPException

from sla_scheduler import (
    get_scheduler_status,
    pause_scheduler,
    resume_scheduler,
    start_scheduler,
    stop_scheduler,
    trigger_scheduler_now,
)

router = APIRouter(prefix="/api/v1/sla", tags=["SLA Scheduler"])


@router.get("/scheduler-status")
def scheduler_status():
    return get_scheduler_status()


@router.post("/scheduler/start")
def scheduler_start():
    return start_scheduler()


@router.post("/scheduler/pause")
def scheduler_pause():
    return pause_scheduler()


@router.post("/scheduler/resume")
def scheduler_resume():
    return resume_scheduler()


@router.post("/scheduler/stop")
def scheduler_stop():
    return stop_scheduler()


@router.post("/scheduler/trigger")
def scheduler_trigger():
    try:
        return trigger_scheduler_now()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
