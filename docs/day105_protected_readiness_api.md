# Day 105 - Protected Readiness API

## Endpoint

`GET /api/v1/readiness`

Authentication: Required. Uses the existing JWT authentication dependency.

## Purpose

Provides a compact operational readiness summary based on the existing
system diagnostics collector.

## Response fields

- `service`: service name
- `ready`: true only when the diagnostic status is healthy and no checks are degraded
- `status`: healthy or degraded
- `timestamp`: diagnostics collection timestamp
- `checks.total`: total diagnostic checks
- `checks.healthy`: healthy checks
- `checks.degraded`: degraded checks

## Security

- Requires an authenticated user.
- Does not expose environment variables, credentials, or secret values.
- Reuses the existing diagnostics collector.
- Does not change the existing health or diagnostics endpoints.

## Validation

Automated tests cover:
- Unauthorized requests
- Healthy readiness response
- Degraded readiness response
