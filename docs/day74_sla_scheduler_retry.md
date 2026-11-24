# Day 74 - SLA Scheduler Retry and Backoff

Added an independent retry utility for temporary job failures.

Features:
- Configurable maximum attempts.
- Configurable initial delay.
- Exponential backoff multiplier.
- Success and failure result details.
- Input validation.

The helper is independently tested and is not yet wired into the live scheduler.
Retrying live SLA jobs requires care because alert generation may have side effects.
