# Day 61 - SLA Breach Alerts and Escalation

## Features
- Detects overdue open incidents using severity-based SLA targets.
- Generates persistent SLA breach alerts.
- Prevents duplicate active alerts for the same incident.
- Updates existing alerts when escalation level changes.
- Supports filtering active/resolved alerts.
- Supports resolving alerts.

## API endpoints

GET /api/v1/sla/alerts
GET /api/v1/sla/alerts?status=active
POST /api/v1/sla/alerts/generate
PATCH /api/v1/sla/alerts/{alert_id}/resolve

## Escalation policy
- Critical: 1 hour target
- High: 4 hour target
- Medium: 24 hour target
- Low: 72 hour target

An incident overdue by at least its full SLA target receives critical escalation.
Other breaches receive priority escalation based on severity.

## Storage
backend/logs/sla_alerts.json

## Notes
Alert generation runs when the alert-list endpoint is requested and
when the explicit generate endpoint is called. This is not a background
scheduler. Production deployment should use a persistent database,
scheduled worker, and authenticated role-based access.
