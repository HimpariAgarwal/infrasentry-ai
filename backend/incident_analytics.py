from collections import Counter
from datetime import datetime, timezone, timedelta

from backend.incident_manager import load_incidents


def generate_incident_analytics():
    incidents = load_incidents()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)

    severity_counts = Counter()
    status_counts = Counter()
    daily_counts = Counter()
    recent_incidents = []

    for incident in incidents:
        severity_counts[incident.get("severity", "unknown")] += 1
        status_counts[incident.get("status", "unknown")] += 1

        try:
            created = datetime.fromisoformat(
                incident["created_at"].replace("Z", "+00:00")
            )
        except (ValueError, KeyError, TypeError):
            continue

        if created >= cutoff:
            day = created.strftime("%Y-%m-%d")
            daily_counts[day] += 1
            recent_incidents.append(incident)

    total = len(incidents)
    resolved = status_counts.get("resolved", 0)

    resolution_rate = round((resolved / total) * 100, 2) if total else 0

    daily_trend = [
        {
            "date": (now - timedelta(days=offset)).strftime("%Y-%m-%d"),
            "count": daily_counts.get(
                (now - timedelta(days=offset)).strftime("%Y-%m-%d"), 0
            ),
        }
        for offset in range(6, -1, -1)
    ]

    return {
        "total_incidents": total,
        "open_incidents": status_counts.get("open", 0),
        "investigating_incidents": status_counts.get("investigating", 0),
        "resolved_incidents": resolved,
        "resolution_rate": resolution_rate,
        "severity_distribution": dict(severity_counts),
        "status_distribution": dict(status_counts),
        "daily_trend": daily_trend,
        "last_7_days_count": len(recent_incidents),
        "generated_at": now.isoformat(),
    }
