from datetime import datetime, timedelta, timezone
from backend.incident_manager import load_incidents

SLA_HOURS = {
    "critical": 1,
    "high": 4,
    "medium": 24,
    "low": 72,
}

def parse_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (ValueError, TypeError):
        return None

def generate_sla_report():
    incidents = load_incidents()
    now = datetime.now(timezone.utc)

    total = len(incidents)
    resolved = 0
    overdue = 0
    within_sla = 0
    invalid_dates = 0
    items = []

    for incident in incidents:
        severity = str(incident.get("severity", "medium")).lower()
        hours = SLA_HOURS.get(severity, 24)

        created = parse_datetime(
            incident.get("created_at") or incident.get("timestamp")
        )

        status = str(incident.get("status", "open")).lower()
        is_resolved = status == "resolved"

        if is_resolved:
            resolved += 1

        if not created:
            invalid_dates += 1
            items.append({
                "incident_id": incident.get("id"),
                "severity": severity,
                "status": status,
                "sla_hours": hours,
                "sla_deadline": None,
                "sla_status": "unknown",
                "message": "Creation timestamp unavailable",
            })
            continue

        deadline = created + timedelta(hours=hours)
        reference_time = parse_datetime(incident.get("updated_at")) if is_resolved else now

        # For unresolved incidents, compare with current time.
        # For resolved incidents, use updated_at when available.
        if reference_time is None:
            reference_time = now

        breached = reference_time > deadline

        if breached:
            overdue += 1
        else:
            within_sla += 1

        items.append({
            "incident_id": incident.get("id"),
            "severity": severity,
            "status": status,
            "sla_hours": hours,
            "sla_deadline": deadline.isoformat(),
            "sla_status": "breached" if breached else "within_sla",
            "message": "SLA deadline exceeded" if breached else "Within SLA",
        })

    known = total - invalid_dates
    compliance = round((within_sla / known) * 100, 2) if known else 0

    return {
        "total_incidents": total,
        "resolved_incidents": resolved,
        "overdue_incidents": overdue,
        "within_sla": within_sla,
        "unknown_sla": invalid_dates,
        "sla_compliance_rate": compliance,
        "severity_sla_hours": SLA_HOURS,
        "incidents": items,
        "generated_at": now.isoformat(),
    }
