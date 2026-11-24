# Day 51 - Automated Security Alerts

## Features
- Generates alerts from threat-analysis results.
- Detects high-risk activity and repeated suspicious IP events.
- Avoids duplicate active alerts.
- Stores alert history in a JSON file.
- Supports resolving alerts.

## API
- POST /api/v1/security/alerts/generate
- GET /api/v1/security/alerts
- PATCH /api/v1/security/alerts/{alert_id}/resolve

## Limitations
Alerts are based on simple event-count heuristics.
They are not real-time firewall actions or proof of malicious activity.
