# Day 89 - SLA Retry Profile Comparison API

## Overview
Added a read-only comparison endpoint for the configured retry profiles.

## Endpoint
GET `/api/v1/sla/retry-comparison/`

## Compared values
- Maximum attempts
- Initial delay
- Backoff factor
- Total accumulated waiting time

## Profiles
- fast
- standard
- conservative

## Safety
The endpoint only reads profile configuration and calculates timing.
It does not execute retries or change profile settings.

## Tests
Run:

`python -m unittest backend.test_sla_scheduler_retry_comparison backend.test_sla_scheduler_retry_comparison_api -v`
