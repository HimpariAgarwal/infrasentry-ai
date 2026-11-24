# Day 83 - SLA Scheduler Retry Policy

## Features
- Classifies timeout and connection errors as retryable.
- Classifies permission, value and type errors as permanent.
- Prevents retries after the configured attempt limit.
- Validates attempt numbers and maximum attempts.

## Safety
The policy is intentionally conservative.
Unknown exception types are permanent by default.
This module is independent and does not yet change live scheduler retry behaviour.

## Verification
Run:
python backend/test_sla_scheduler_retry_policy.py
