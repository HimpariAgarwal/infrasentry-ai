# Day 54 - Security Incident Management

## Features
- Convert active security alerts into incident records.
- Prevent duplicate incident creation from the same alert.
- Filter incidents by status.
- Update incident status and assignee.
- Add investigation notes.

## API
- POST /api/v1/incidents/from-alerts
- GET /api/v1/incidents
- PATCH /api/v1/incidents/{incident_id}

## Status values
- open
- investigating
- resolved

## Storage
Incident records are stored in backend/logs/security_incidents.json.
