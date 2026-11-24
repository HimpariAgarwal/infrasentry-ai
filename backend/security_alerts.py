import json
from datetime import datetime, timezone
from pathlib import Path

from backend.threat_detection import analyze_security_events

ALERT_FILE = Path(__file__).resolve().parent / "logs" / "security_alerts.json"


def load_alerts():
    if not ALERT_FILE.exists():
        return []
    try:
        return json.loads(ALERT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def generate_security_alerts():
    analysis = analyze_security_events()
    alerts = load_alerts()
    generated = []

    if analysis["risk_level"] == "high":
        generated.append({
            "type": "HIGH_RISK_ACTIVITY",
            "severity": "critical",
            "message": "High volume of suspicious security events detected.",
            "source": "threat_detection",
        })

    for item in analysis["suspicious_ips"]:
        generated.append({
            "type": "SUSPICIOUS_IP",
            "severity": item["risk"],
            "message": f"Repeated security events from {item['ip_address']}",
            "source": item["ip_address"],
            "event_count": item["event_count"],
        })

    existing = {
        (alert.get("type"), alert.get("source"))
        for alert in alerts
        if alert.get("status") == "active"
    }

    new_alerts = []
    for item in generated:
        key = (item["type"], item["source"])
        if key in existing:
            continue

        alert = {
            "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            **item,
        }
        alerts.insert(0, alert)
        new_alerts.append(alert)
        existing.add(key)

    ALERT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ALERT_FILE.write_text(
        json.dumps(alerts[:500], indent=2),
        encoding="utf-8",
    )

    return {
        "generated_count": len(new_alerts),
        "total_alerts": len(alerts),
        "alerts": new_alerts,
    }


def get_security_alerts():
    return load_alerts()


def resolve_security_alert(alert_id):
    alerts = load_alerts()
    found = False

    for alert in alerts:
        if alert.get("id") == alert_id:
            alert["status"] = "resolved"
            alert["resolved_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            break

    if found:
        ALERT_FILE.parent.mkdir(parents=True, exist_ok=True)
        ALERT_FILE.write_text(json.dumps(alerts, indent=2), encoding="utf-8")

    return found
