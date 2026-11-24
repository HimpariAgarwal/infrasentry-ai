import logging
from threading import Lock

from apscheduler.schedulers.background import BackgroundScheduler

from backend.sla_alerts import generate_sla_alerts

logger = logging.getLogger("infrasentry.sla_scheduler")

_scheduler = None
_scheduler_lock = Lock()


def run_sla_escalation_job():
    """Generate overdue SLA alerts periodically."""
    try:
        result = generate_sla_alerts()
        logger.info("SLA escalation job completed: %s", result)
    except Exception:
        logger.exception("SLA escalation job failed")


def start_sla_scheduler():
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None and _scheduler.running:
            return

        scheduler = BackgroundScheduler(
            timezone="UTC",
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 30,
            },
        )

        scheduler.add_job(
            run_sla_escalation_job,
            trigger="interval",
            seconds=60,
            id="infrasentry_sla_escalation",
            replace_existing=True,
            next_run_time=None,
        )

        scheduler.start()
        _scheduler = scheduler
        logger.info("SLA escalation scheduler started (60-second interval).")


def stop_sla_scheduler():
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None and _scheduler.running:
            _scheduler.shutdown(wait=False)
            logger.info("SLA escalation scheduler stopped.")

        _scheduler = None


def get_sla_scheduler_status():
    scheduler = _scheduler
    if scheduler is None or not scheduler.running:
        return {"running": False, "interval_seconds": 60}

    job = scheduler.get_job("infrasentry_sla_escalation")
    return {
        "running": True,
        "interval_seconds": 60,
        "next_run_time": job.next_run_time.isoformat() if job and job.next_run_time else None,
    }
