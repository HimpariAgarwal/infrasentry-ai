import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

METRICS_FILE = Path(__file__).resolve().parent / "logs" / "sla_scheduler_metrics.json"
_lock = threading.Lock()


def _load_metrics():
    if not METRICS_FILE.exists():
        return {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_duration_ms": 0.0,
            "average_duration_ms": 0.0,
            "last_run": None,
            "last_status": "not_run",
            "history": [],
        }

    try:
        data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Invalid metrics format")
        return data
    except (OSError, ValueError, json.JSONDecodeError):
        return {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_duration_ms": 0.0,
            "average_duration_ms": 0.0,
            "last_run": None,
            "last_status": "not_run",
            "history": [],
        }


def record_scheduler_run(status, duration_ms, message=None):
    with _lock:
        data = _load_metrics()
        data["total_runs"] += 1

        if status == "success":
            data["successful_runs"] += 1
        else:
            data["failed_runs"] += 1

        data["total_duration_ms"] = round(
            data["total_duration_ms"] + duration_ms, 2
        )
        data["average_duration_ms"] = round(
            data["total_duration_ms"] / data["total_runs"], 2
        )

        timestamp = datetime.now(timezone.utc).isoformat()
        data["last_run"] = timestamp
        data["last_status"] = status

        data.setdefault("history", []).append({
            "timestamp": timestamp,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "message": message,
        })

        data["history"] = data["history"][-100:]

        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp_file = METRICS_FILE.with_suffix(".tmp")
        temp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_file.replace(METRICS_FILE)

        return data


def get_scheduler_metrics():
    with _lock:
        data = _load_metrics()

    return {
        "total_runs": data.get("total_runs", 0),
        "successful_runs": data.get("successful_runs", 0),
        "failed_runs": data.get("failed_runs", 0),
        "average_duration_ms": data.get("average_duration_ms", 0),
        "last_run": data.get("last_run"),
        "last_status": data.get("last_status", "not_run"),
        "history": data.get("history", [])[-20:],
        "retained_history": len(data.get("history", [])),
    }
