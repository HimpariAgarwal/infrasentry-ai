# Day 40 - API Rate Limiting

## Security Feature
InfraSentry AI now includes API request rate limiting.

## Configuration
- Maximum requests: 120
- Time window: 60 seconds
- Scope: /api/* endpoints
- Excess requests: HTTP 429
- Retry-After header included

## Response Headers
- X-RateLimit-Limit
- X-RateLimit-Remaining
- Retry-After (when blocked)

## Implementation
backend/rate_limit.py

Integrated through FastAPI middleware in backend/main.py.

## Limitation
This implementation uses in-memory, per-process storage.
For multi-worker or distributed deployments, use a shared
rate-limit store such as Redis.
