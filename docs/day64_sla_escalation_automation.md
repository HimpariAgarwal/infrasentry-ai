# Day 64 — SLA Escalation Automation

## Features
- APScheduler background scheduler.
- Generates SLA escalation alerts every 60 seconds.
- Uses existing SLA alert generation and deduplication logic.
- Starts and stops with the FastAPI application lifecycle.
- Scheduler status endpoint:
  GET /api/v1/sla/scheduler-status

## Operational notes
- Scheduler runs inside the FastAPI process.
- In-memory scheduling is suitable for a single application worker.
- Multiple workers or multiple backend replicas can run duplicate jobs;
  use a dedicated scheduler process or distributed lock in production.
- Alert generation depends on the existing incident and SLA data.
