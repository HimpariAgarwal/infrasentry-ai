import json
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "logs" / "security_audit.log"


def analyze_security_events():
    if not LOG_FILE.exists():
        return {
            "total_events": 0,
            "unique_ips": 0,
            "suspicious_ips": [],
            "risk_level": "low",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    events = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            try:
                item = json.loads(line)
                timestamp = datetime.fromisoformat(
                    item.get("timestamp", "").replace("Z", "+00:00")
                )
                if timestamp >= cutoff:
                    events.append(item)
            except (ValueError, TypeError, json.JSONDecodeError):
                continue

    ip_counts = Counter(
        item.get("ip_address", "unknown")
        for item in events
        if item.get("ip_address")
    )

    suspicious = []
    for ip, count in ip_counts.items():
        if ip != "unknown" and count >= 5:
            suspicious.append({
                "ip_address": ip,
                "event_count": count,
                "risk": "high" if count >= 15 else "medium",
            })

    suspicious.sort(key=lambda item: item["event_count"], reverse=True)

    total = len(events)
    if any(item["event_count"] >= 15 for item in suspicious):
        risk = "high"
    elif suspicious:
        risk = "medium"
    else:
        risk = "low"

    return {
        "total_events": total,
        "unique_ips": len(ip_counts),
        "suspicious_ips": suspicious,
        "risk_level": risk,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_window": "24 hours",
    }
