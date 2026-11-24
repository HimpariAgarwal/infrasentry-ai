# Day 59 - SLA Monitoring

## SLA targets

| Severity | Response target |
|---|---:|
| Critical | 1 hour |
| High | 4 hours |
| Medium | 24 hours |
| Low | 72 hours |

## API

GET /api/v1/sla/report

Requires JWT authentication.

Returns incident-level SLA status, overdue count, unknown timestamps and compliance rate.

## Important limitation

This initial version estimates SLA compliance using incident creation and resolution/update timestamps. It does not yet record the exact first-response time. Treat it as an operational estimate, not an audited SLA measurement.
