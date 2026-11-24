import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

INCIDENT_FILE = Path(__file__).resolve().parent / "logs" / "security_incidents.json"


def load_incidents():
    if not INCIDENT_FILE.exists():
        return []
    try:
        return json.loads(INCIDENT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_incidents(incidents):
    INCIDENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    INCIDENT_FILE.write_text(
        json.dumps(incidents[:1000], indent=2),
        encoding="utf-8",
    )


def create_incident(data):
    incidents = load_incidents()

    if any(item.get("alert_id") == data.get("id") for item in incidents):
        return None

    incident = {
        "id": str(uuid.uuid4()),
        "alert_id": data.get("id"),
        "title": data.get("type", "Security Incident").replace("_", " "),
        "description": data.get("message", ""),
        "severity": data.get("severity", "medium"),
        "source": data.get("source", "unknown"),
        "status": "open",
        "assigned_to": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "notes": [],
    }

    incidents.insert(0, incident)
    save_incidents(incidents)
    return incident


def list_incidents(status="all"):
    incidents = load_incidents()
    if status != "all":
        incidents = [
            item for item in incidents
            if item.get("status") == status
        ]
    return incidents


def update_incident(incident_id, updates):
    incidents = load_incidents()

    for item in incidents:
        if item.get("id") == incident_id:
            if "status" in updates:
                item["status"] = updates["status"]
            if "assigned_to" in updates:
                item["assigned_to"] = updates["assigned_to"]
            if "note" in updates and updates["note"]:
                item["notes"].append({
                    "text": updates["note"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            item["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_incidents(incidents)
            return item

    return None
