import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from threading import Lock

from backend.incident_manager import load_incidents

BASE_DIR = Path(__file__).resolve().parent
ALERT_FILE = BASE_DIR / "logs" / "sla_alerts.json"
LOCK = Lock()

SLA_HOURS = {
    "critical": 1,
    "high": 4,
    "medium": 24,
    "low": 72,
}

def now_utc():
    return datetime.now(timezone.utc)

def parse_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None

def read_alerts():
    if not ALERT_FILE.exists():
        return []
    try:
        data = json.loads(ALERT_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_alerts(alerts):
    ALERT_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = ALERT_FILE.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(alerts, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    temp_file.replace(ALERT_FILE)

def get_incident_time(incident):
    return (
        parse_datetime(incident.get("created_at"))
        or parse_datetime(incident.get("timestamp"))
        or parse_datetime(incident.get("createdAt"))
    )

def evaluate_incident(incident, current_time):
    severity = str(incident.get("severity", "medium")).lower()
    severity = severity if severity in SLA_HOURS else "medium"

    status = str(incident.get("status", "open")).lower()
    if status in ("resolved", "closed", "completed"):
        return None

    created = get_incident_time(incident)
    if not created:
        return None

    target_hours = SLA_HOURS[severity]
    elapsed_hours = max(0, (current_time - created).total_seconds() / 3600)
    if elapsed_hours <= target_hours:
        return None

    overdue_hours = elapsed_hours - target_hours

    if overdue_hours >= target_hours:
        escalation = "critical"
        escalation_message = "Immediate escalation required"
    elif severity in ("critical", "high"):
        escalation = "high"
        escalation_message = "Priority escalation required"
    else:
        escalation = "medium"
        escalation_message = "SLA breach detected"

    return {
        "incident_id": str(incident.get("id", incident.get("incident_id", "unknown"))),
        "incident_title": str(incident.get("title", incident.get("name", "Untitled incident"))),
        "severity": severity,
        "status": status,
        "target_hours": target_hours,
        "elapsed_hours": round(elapsed_hours, 2),
        "overdue_hours": round(overdue_hours, 2),
        "escalation_level": escalation,
        "escalation_message": escalation_message,
    }

def generate_sla_alerts():
    current_time = now_utc()
    incidents = load_incidents() or []
    generated = []

    with LOCK:
        alerts = read_alerts()

        for incident in incidents:
            if not isinstance(incident, dict):
                continue

            evaluation = evaluate_incident(incident, current_time)
            if not evaluation:
                continue

            incident_id = evaluation["incident_id"]

            existing = next(
                (
                    alert for alert in alerts
                    if alert.get("incident_id") == incident_id
                    and alert.get("status") == "active"
                ),
                None
            )

            if existing:
                existing.update(evaluation)
                existing["last_checked_at"] = current_time.isoformat()
                continue

            alert = {
                "id": f"SLA-{incident_id}-{int(current_time.timestamp())}",
                **evaluation,
                "alert_type": "sla_breach",
                "status": "active",
                "created_at": current_time.isoformat(),
                "last_checked_at": current_time.isoformat(),
                "resolved_at": None,
            }

            alerts.insert(0, alert)
            generated.append(alert)

        save_alerts(alerts)

    return {
        "generated": len(generated),
        "total_active": sum(1 for a in alerts if a.get("status") == "active"),
        "alerts": generated,
    }

def get_sla_alerts(status=None):
    # Refresh breach detection whenever the dashboard requests alerts.
    generate_sla_alerts()

    alerts = read_alerts()
    if status:
        alerts = [a for a in alerts if a.get("status") == status.lower()]
    return alerts

def resolve_sla_alert(alert_id):
    with LOCK:
        alerts = read_alerts()
        for alert in alerts:
            if alert.get("id") == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = now_utc().isoformat()
                save_alerts(alerts)
                return alert
    return None
