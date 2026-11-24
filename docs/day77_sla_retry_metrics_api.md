# Day 77 - SLA Retry Metrics API

Added a FastAPI router exposing:

GET /api/v1/sla/retry-metrics

The endpoint returns:
- Total retry runs
- Successful and failed runs
- Total attempts
- Average execution duration
- Last execution
- Recent execution history

The endpoint returns HTTP 500 if metrics retrieval fails.

The router is intentionally standalone in this task.
It has not yet been registered in backend/main.py.
Register it in a later integration task after verifying the application's
existing router and authentication conventions.
