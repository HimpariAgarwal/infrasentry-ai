import json
import threading
from datetime import datetime, timezone
from pathlib import Path

METRICS_FILE = Path(__file__).resolve().parent / "logs" / "sla_scheduler_retry_metrics.json"
_LOCK = threading.Lock()
MAX_HISTORY = 100


def _empty_metrics():
    return {
        "total_runs": 0,
        "successful_runs": 0,
        "failed_runs": 0,
        "total_attempts": 0,
        "average_duration_seconds": 0.0,
        "last_run": None,
        "history": [],
    }


def get_retry_metrics():
    with _LOCK:
        if not METRICS_FILE.exists():
            return _empty_metrics()

        try:
            data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return _empty_metrics()
            return {**_empty_metrics(), **data}
        except (OSError, json.JSONDecodeError):
            return _empty_metrics()


def record_retry_run(status, attempts, duration_seconds, error=None):
    if status not in ("success", "failed"):
        raise ValueError("status must be 'success' or 'failed'")
    if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 1:
        raise ValueError("attempts must be a positive integer")
    if not isinstance(duration_seconds, (int, float)) or duration_seconds < 0:
        raise ValueError("duration_seconds must be a non-negative number")

    with _LOCK:
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

        if METRICS_FILE.exists():
            try:
                data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    data = _empty_metrics()
            except (OSError, json.JSONDecodeError):
                data = _empty_metrics()
        else:
            data = _empty_metrics()

        data = {**_empty_metrics(), **data}

        total = data["total_runs"] + 1
        previous_duration = (
            data["average_duration_seconds"] * data["total_runs"]
        )
        average = (previous_duration + float(duration_seconds)) / total

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "attempts": attempts,
            "duration_seconds": round(float(duration_seconds), 4),
            "error": str(error) if error is not None else None,
        }

        data["total_runs"] = total
        data["successful_runs"] += int(status == "success")
        data["failed_runs"] += int(status == "failed")
        data["total_attempts"] += attempts
        data["average_duration_seconds"] = round(average, 4)
        data["last_run"] = entry
        data["history"] = (data["history"] + [entry])[-MAX_HISTORY:]

        temp_file = METRICS_FILE.with_suffix(".tmp")
        temp_file.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
        temp_file.replace(METRICS_FILE)

        return data
