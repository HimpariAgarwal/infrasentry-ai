# Day 88 - SLA Retry Profile Execution Preview API

## Overview
Added a read-only API to preview retry timing for configured SLA retry profiles.

## Endpoint
GET `/api/v1/sla/retry-preview/{profile_name}`

Supported profiles:
- fast
- standard
- conservative

## Response
The response includes:
- Profile name
- Maximum attempts
- Initial delay
- Backoff factor
- Total accumulated waiting time
- Per-attempt delay and cumulative waiting time

## Safety
This endpoint only calculates a schedule. It does not execute retries,
trigger SLA alerts, or modify retry profile configuration.

Unknown profiles return HTTP 404.

## Tests
Run the preview service, API, and router integration tests:

`python -m unittest backend.test_sla_scheduler_retry_preview backend.test_sla_scheduler_retry_preview_api backend.test_sla_scheduler_retry_preview_integration -v`
