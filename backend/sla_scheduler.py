from sla_scheduler_reliability import prevent_overlapping_runs
from datetime import datetime, timezone
from threading import RLock

from apscheduler.schedulers.background import BackgroundScheduler

from sla_alerts import generate_sla_alerts
from sla_scheduler_metrics import record_scheduler_run
from sla_scheduler_retry_execution import execute_sla_generation_with_retry

_scheduler = BackgroundScheduler(timezone="UTC")
_lock = RLock()
_job_id = "sla_alert_generation"


@prevent_overlapping_runs
def _run_sla_job():
    started = datetime.now(timezone.utc)
    try:
        result = execute_sla_generation_with_retry(generate_sla_alerts)
        record_scheduler_run(
            status="success",
            duration_seconds=(datetime.now(timezone.utc) - started).total_seconds(),
            details={"result": str(result)[:500]},
        )
        return result
    except Exception as exc:
        record_scheduler_run(
            status="failure",
            duration_seconds=(datetime.now(timezone.utc) - started).total_seconds(),
            details={"error": str(exc)[:500]},
        )
        raise


def start_scheduler():
    with _lock:
        if not _scheduler.running:
            _scheduler.add_job(
                _run_sla_job,
                trigger="interval",
                seconds=60,
                id=_job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
            _scheduler.start()
        elif _scheduler.get_job(_job_id) is None:
            _scheduler.add_job(
                _run_sla_job,
                trigger="interval",
                seconds=60,
                id=_job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
        return get_scheduler_status()


def pause_scheduler():
    with _lock:
        if _scheduler.running and _scheduler.get_job(_job_id):
            _scheduler.pause_job(_job_id)
        return get_scheduler_status()


def resume_scheduler():
    with _lock:
        if not _scheduler.running:
            return start_scheduler()
        job = _scheduler.get_job(_job_id)
        if job is None:
            _scheduler.add_job(
                _run_sla_job,
                trigger="interval",
                seconds=60,
                id=_job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
        else:
            _scheduler.resume_job(_job_id)
        return get_scheduler_status()


def trigger_scheduler_now():
    with _lock:
        if not _scheduler.running:
            raise RuntimeError("Scheduler is not running")
        job = _scheduler.get_job(_job_id)
        if job is None:
            raise RuntimeError("SLA scheduler job is not configured")
        _scheduler.modify_job(_job_id, next_run_time=datetime.now(timezone.utc))
        return {"triggered": True, "message": "SLA job scheduled immediately"}


def get_scheduler_status():
    with _lock:
        job = _scheduler.get_job(_job_id) if _scheduler.running else None
        paused = bool(_scheduler.running and job is not None and job.next_run_time is None)
        return {
            "running": _scheduler.running,
            "paused": paused,
            "job_configured": job is not None,
            "job_id": _job_id,
            "interval_seconds": 60,
            "next_run_time": (
                job.next_run_time.isoformat()
                if job is not None and job.next_run_time is not None
                else None
            ),
        }


def stop_scheduler():
    with _lock:
        if _scheduler.running:
            _scheduler.shutdown(wait=False)
        return get_scheduler_status()

