# Day 85 - SLA Retry Configuration Profiles

## Profiles
- Fast: 2 attempts, 0.5 second initial delay, factor 2.
- Standard: 3 attempts, 1 second initial delay, factor 2.
- Conservative: 3 attempts, 3 second initial delay, factor 3.

## Features
- Immutable retry configuration.
- Case-insensitive profile lookup.
- Rejects invalid profile configuration.
- Executes through the Day 84 policy-aware retry engine.
- Standard is the default profile.

## Safety
Profiles are independent configuration options.
The live SLA scheduler is not automatically switched to any profile.
Permanent errors remain non-retryable through the Day 83 policy.

## Verification
python backend/test_sla_scheduler_retry_profiles.py
